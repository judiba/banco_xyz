# faiss_query_store_s3.py
import os
import json
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
import faiss
import boto3

from bedrock_embeddings import TitanEmbedder, AWS_REGION, EMBEDDING_MODEL_ID

FAISS_DIR = os.getenv("FAISS_DIR", "./faiss_store")
FAISS_INDEX_PATH = os.path.join(FAISS_DIR, "queries.index")
FAISS_META_PATH = os.path.join(FAISS_DIR, "queries_meta.json")

S3_BUCKET = os.getenv("S3_BUCKET", "")
S3_KEY = os.getenv("S3_KEY", "")  # ex.: "path/to/queries.json"
S3_PREFIX = os.getenv("S3_PREFIX", "")  # opcional: lista vários JSONs


def _normalize_rows(x: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(x, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    return x / norms


class FaissQueryStore:
    """
    Índice FAISS (IndexFlatIP) + metadados JSON.
    Cada item deve ter ao menos: {id, query_text, description}
    """

    def __init__(self, index_path: str = FAISS_INDEX_PATH, meta_path: str = FAISS_META_PATH):
        self.index_path = index_path
        self.meta_path = meta_path
        self.index: Optional[faiss.Index] = None
        self.meta: List[Dict[str, Any]] = []
        self.dim: Optional[int] = None
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)

    def exists(self) -> bool:
        return os.path.isfile(self.index_path) and os.path.isfile(self.meta_path)

    def load(self):
        if not self.exists():
            raise FileNotFoundError(
                "Índice FAISS/metadados não encontrados. Rode o bootstrap antes."
            )
        self.index = faiss.read_index(self.index_path)
        with open(self.meta_path, "r", encoding="utf-8") as f:
            self.meta = json.load(f)
        if hasattr(self.index, "d"):
            self.dim = self.index.d
        else:
            raise RuntimeError("Não foi possível inferir a dimensão do índice FAISS.")

    def _read_jsons_from_s3(
        self, bucket: str, key: str = "", prefix: str = ""
    ) -> List[Dict[str, Any]]:
        """
        Lê um ou vários JSONs do S3. Cada JSON deve ser uma lista de objetos.
        """
        s3 = boto3.client("s3")
        items: List[Dict[str, Any]] = []

        if key:
            obj = s3.get_object(Bucket=bucket, Key=key)
            payload = json.loads(obj["Body"].read().decode("utf-8"))
            if isinstance(payload, list):
                items.extend(payload)
            else:
                raise ValueError("JSON deve ser uma lista de objetos.")
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

        # Normaliza e valida
        data = []
        for it in items:
            if "query_text" not in it:
                continue
            if "id" not in it:
                it["id"] = f"q_{len(data)+1:04d}"
            data.append(it)
        if not data:
            raise ValueError("Nenhum item válido encontrado em S3 (faltou 'query_text').")
        return data

    def build_from_s3(
        self, bucket: str, key: str = "", prefix: str = "", embedder: TitanEmbedder = None
    ):
        """
        Constrói índice FAISS do zero usando JSON(s) no S3.
        """
        if embedder is None:
            embedder = TitanEmbedder(region_name=AWS_REGION, model_id=EMBEDDING_MODEL_ID)

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
        self, bucket: str, key: str = "", prefix: str = "", embedder: TitanEmbedder = None
    ) -> Tuple[int, int]:
        """
        Atualiza índice existente com novos itens do S3 (evita duplicar 'id').
        Retorna (novos_itens_adicionados, total_itens_resultantes).
        """
        if embedder is None:
            embedder = TitanEmbedder(region_name=AWS_REGION, model_id=EMBEDDING_MODEL_ID)
        if not self.exists():
            # Se não existe, constrói do zero
            self.build_from_s3(bucket=bucket, key=key, prefix=prefix, embedder=embedder)
            return (len(self.meta), len(self.meta))

        self.load()
        current_ids = {m["id"] for m in self.meta}

        new_items = self._read_jsons_from_s3(bucket=bucket, key=key, prefix=prefix)
        new_items = [it for it in new_items if it["id"] not in current_ids]
        if not new_items:
            return (0, len(self.meta))

        # Embeddings novos
        texts = [d["query_text"] for d in new_items]
        new_embeds = embedder.embed_texts(texts).astype("float32")
        new_embeds_norm = _normalize_rows(new_embeds)

        # Concatena no índice
        self.index.add(new_embeds_norm)
        self.meta.extend(new_items)

        # Persiste novamente
        faiss.write_index(self.index, self.index_path)
        with open(self.meta_path, "w", encoding="utf-8") as f:
            json.dump(self.meta, f, ensure_ascii=False, indent=2)

        return (len(new_items), len(self.meta))

    def search(
        self, query_text: str, embedder: TitanEmbedder, top_k: int = 5
    ) -> List[Dict[str, Any]]:
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


def bootstrap_from_s3():
    """
    CLI: constrói índice FAISS a partir do S3.
    Use variáveis de ambiente S3_BUCKET + (S3_KEY ou S3_PREFIX).
    """
    bucket = S3_BUCKET
    key = S3_KEY
    prefix = S3_PREFIX
    if not bucket:
        raise ValueError("Defina S3_BUCKET.")
    store = FaissQueryStore(index_path=FAISS_INDEX_PATH, meta_path=FAISS_META_PATH)
    embedder = TitanEmbedder(region_name=AWS_REGION, model_id=EMBEDDING_MODEL_ID)
    store.build_from_s3(bucket=bucket, key=key, prefix=prefix, embedder=embedder)
    print(f"[Bootstrap] Índice gravado: {FAISS_INDEX_PATH}")
    print(f"[Bootstrap] Metadados gravados: {FAISS_META_PATH}")


if __name__ == "__main__":
    bootstrap_from_s3()
