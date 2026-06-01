# scripts/agents/rag_to_sql_tool_agentcore.py
from __future__ import annotations

import os
import json
from typing import List, Dict, Any, Optional, Tuple

import numpy as np
import boto3

# ---- Dependência FAISS ----
# Em Lambda, FAISS deve estar em um Layer compatível (ou mude p/ container).
import faiss
from strands import tool

# ------------------------------------------------------------
# Config (via variáveis de ambiente)
# ------------------------------------------------------------
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
EMBEDDING_MODEL_ID = os.getenv("EMBEDDING_MODEL_ID", "amazon.titan-embed-text-v2")

# Fonte de dados (JSON no S3)
S3_BUCKET = os.getenv("S3_BUCKET", "")
S3_KEY = os.getenv("S3_KEY", "")  # ex.: path/queries.json
S3_PREFIX = os.getenv("S3_PREFIX", "")  # alternativa: prefixo com vários JSONs

# Persistência do índice
FAISS_DIR = os.getenv("FAISS_DIR", "/tmp/faiss_store")  # /tmp em Lambda
FAISS_INDEX_PATH = os.path.join(FAISS_DIR, "queries.index")
FAISS_META_PATH = os.path.join(FAISS_DIR, "queries_meta.json")

os.makedirs(FAISS_DIR, exist_ok=True)


# ------------------------------------------------------------
# Titan Embeddings (Bedrock)
# ------------------------------------------------------------
class TitanEmbedder:
    """
    Gera embeddings de texto usando Amazon Titan via Bedrock Runtime.
    Padrão: amazon.titan-embed-text-v2 (recomendado para texto puro).
    """

    def __init__(self, region_name: Optional[str] = None, model_id: Optional[str] = None):
        self.region_name = region_name or AWS_REGION
        self.model_id = model_id or EMBEDDING_MODEL_ID
        self.client = boto3.client("bedrock-runtime", region_name=self.region_name, verify=False)

    def embed_text(self, text: str) -> List[float]:
        body = {"inputText": text}
        resp = self.client.invoke_model(
            modelId=self.model_id,
            body=json.dumps(body),
            contentType="application/json",
            accept="application/json",
        )
        payload = json.loads(resp["body"].read())
        return payload["embedding"]

    def embed_texts(self, texts: List[str]) -> np.ndarray:
        vecs = [self.embed_text(t) for t in texts]
        return np.array(vecs, dtype="float32")


# ------------------------------------------------------------
# FAISS store (cosine via inner product + normalização)
# ------------------------------------------------------------
def _normalize_rows(x: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(x, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    return x / norms


class FaissQueryStore:
    """
    Índice FAISS + metadados JSON.
    Cada item do JSON S3 deve ter: { id?, query_text, description? }
    """

    def __init__(self, index_path: str = FAISS_INDEX_PATH, meta_path: str = FAISS_META_PATH):
        self.index_path = index_path
        self.meta_path = meta_path
        self.index: Optional[faiss.Index] = None
        self.meta: List[Dict[str, Any]] = []
        self.dim: Optional[int] = None

    def exists(self) -> bool:
        return os.path.isfile(self.index_path) and os.path.isfile(self.meta_path)

    def load(self):
        self.index = faiss.read_index(self.index_path)
        with open(self.meta_path, "r", encoding="utf-8") as f:
            self.meta = json.load(f)
        if hasattr(self.index, "d"):
            self.dim = self.index.d
        else:
            raise RuntimeError("Não foi possível inferir a dimensão do índice FAISS.")

    # ---------- S3 IO ----------
    def _read_jsons_from_s3(
        self, bucket: str, key: str = "", prefix: str = ""
    ) -> List[Dict[str, Any]]:
        s3 = boto3.client("s3")
        items: List[Dict[str, Any]] = []

        if key:
            obj = s3.get_object(Bucket=bucket, Key=key)
            payload = json.loads(obj["Body"].read().decode("utf-8"))
            if not isinstance(payload, list):
                raise ValueError("O JSON deve ser uma lista de objetos.")
            items.extend(payload)

        elif prefix:
            paginator = s3.get_paginator("list_objects_v2")
            for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
                for c in page.get("Contents", []):
                    k = c["Key"]
                    if not k.lower().endswith(".json"):
                        continue
                    obj = s3.get_object(Bucket=bucket, Key=k)
                    payload = json.loads(obj["Body"].read().decode("utf-8"))
                    if isinstance(payload, list):
                        items.extend(payload)
        else:
            raise ValueError("Informe S3_KEY ou S3_PREFIX.")

        data: List[Dict[str, Any]] = []
        for it in items:
            if "query_text" not in it:
                continue
            if "id" not in it:
                it["id"] = f"q_{len(data)+1:04d}"
            data.append(it)

        if not data:
            raise ValueError("Nenhum item válido encontrado no S3 (faltou 'query_text').")
        return data

    # ---------- Build / Upsert ----------
    def build_from_s3(
        self, bucket: str, key: str = "", prefix: str = "", embedder: Optional[TitanEmbedder] = None
    ):
        embedder = embedder or TitanEmbedder()
        data = self._read_jsons_from_s3(bucket=bucket, key=key, prefix=prefix)

        texts = [d["query_text"] for d in data]
        embeds = embedder.embed_texts(texts).astype("float32")
        self.dim = embeds.shape[1]

        embeds_norm = _normalize_rows(embeds)
        index = faiss.IndexFlatIP(self.dim)
        index.add(embeds_norm)

        faiss.write_index(index, self.index_path)
        with open(self.meta_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        self.index = index
        self.meta = data

    def upsert_from_s3(
        self, bucket: str, key: str = "", prefix: str = "", embedder: Optional[TitanEmbedder] = None
    ) -> Tuple[int, int]:
        embedder = embedder or TitanEmbedder()
        if not self.exists():
            self.build_from_s3(bucket=bucket, key=key, prefix=prefix, embedder=embedder)
            return (len(self.meta), len(self.meta))

        self.load()
        current_ids = {m["id"] for m in self.meta}

        new_items = self._read_jsons_from_s3(bucket=bucket, key=key, prefix=prefix)
        new_items = [it for it in new_items if it["id"] not in current_ids]
        if not new_items:
            return (0, len(self.meta))

        texts = [d["query_text"] for d in new_items]
        new_embeds = embedder.embed_texts(texts).astype("float32")
        new_embeds_norm = _normalize_rows(new_embeds)

        self.index.add(new_embeds_norm)
        self.meta.extend(new_items)

        faiss.write_index(self.index, self.index_path)
        with open(self.meta_path, "w", encoding="utf-8") as f:
            json.dump(self.meta, f, ensure_ascii=False, indent=2)

        return (len(new_items), len(self.meta))

    # ---------- Search ----------
    def search(
        self, query_text: str, embedder: Optional[TitanEmbedder] = None, top_k: int = 5
    ) -> List[Dict[str, Any]]:
        embedder = embedder or TitanEmbedder()
        if self.index is None:
            self.load()
        q = embedder.embed_texts([query_text]).astype("float32")
        q = _normalize_rows(q)
        scores, idxs = self.index.search(q, top_k)
        results: List[Dict[str, Any]] = []
        for rank, (i, s) in enumerate(zip(idxs[0], scores[0]), start=1):
            if i < 0 or i >= len(self.meta):
                continue
            item = dict(self.meta[i])
            item["score"] = float(s)
            item["rank"] = rank
            results.append(item)
        return results


# ------------------------------------------------------------
# Bootstrap + Tool p/ Agent Core
# ------------------------------------------------------------
_store: Optional[FaissQueryStore] = None
_embedder: Optional[TitanEmbedder] = None


def _bootstrap_if_needed():
    """
    Garante que o índice FAISS esteja disponível.
    Se não existir localmente, constrói a partir do S3 usando as variáveis de ambiente.
    """
    global _store, _embedder
    if _embedder is None:
        _embedder = TitanEmbedder(region_name=AWS_REGION, model_id=EMBEDDING_MODEL_ID)
    if _store is None:
        _store = FaissQueryStore(index_path=FAISS_INDEX_PATH, meta_path=FAISS_META_PATH)
        if _store.exists():
            _store.load()
        else:
            if not S3_BUCKET or (not S3_KEY and not S3_PREFIX):
                raise RuntimeError(
                    "FAISS não encontrado localmente e S3 não configurado. "
                    "Defina S3_BUCKET e S3_KEY (ou S3_PREFIX) no ambiente."
                )
            _store.build_from_s3(bucket=S3_BUCKET, key=S3_KEY, prefix=S3_PREFIX, embedder=_embedder)


# >>> Ajuste este import para o SEU decorador @tool do Agent Core <<<
# Exemplo fictício:
# from agent_core import tool
# Se no seu projeto o decorador já está em escopo, remova o import acima e mantenha apenas @tool.


@tool
def rag_to_sql_context(user_query: str, top_k: int = 5) -> str:
    """
    Recupera exemplos de queries similares (few-shot) do índice FAISS (JSON do S3),
    para enriquecer o prompt do agente Text-to-SQL.
    Retorna um bloco textual com exemplos e scores.
    """
    _bootstrap_if_needed()
    results = _store.search(user_query, embedder=_embedder, top_k=top_k)
    if not results:
        return "Nenhuma query similar encontrada."
    lines: List[str] = []
    for r in results:
        q = r.get("query_text", "").strip()
        desc = r.get("description", "")
        score = r.get("score", 0.0)
        if desc:
            lines.append(f"-- exemplo (score={score:.3f}): {desc}\n{q}")
        else:
            lines.append(f"-- exemplo (score={score:.3f})\n{q}")
    return "\n\n".join(lines)
