from __future__ import annotations
from pathlib import Path
from typing import List
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from app.core.config import CORPUS_DIR, VECTOR_DIR, settings
from app.services.llm_service import get_embeddings

def _load_documents() -> List[Document]:
    docs: List[Document] = []

    print(f"Lendo de: {CORPUS_DIR}")
    paths = list(Path(CORPUS_DIR).glob("*.txt"))
    print(f"Arquivos encontrados: {paths}")

    for path in paths:
        docs.append(
            Document(
                page_content=path.read_text(encoding="utf-8", errors="ignore"),
                metadata={"source": path.name},
            )
        )

    return docs

def ensure_vector_store() -> FAISS:
    VECTOR_DIR.mkdir(parents=True, exist_ok=True)

    embeddings = get_embeddings()
    index_file = VECTOR_DIR / f"{settings.vector_index_name}.faiss"

    if index_file.exists():
        return FAISS.load_local(
            folder_path=str(VECTOR_DIR),
            embeddings=embeddings,
            index_name=settings.vector_index_name,
            allow_dangerous_deserialization=True,
        )

    docs = _load_documents()
    print(f"Documentos carregados: {len(docs)}")

    if not docs:
        raise RuntimeError(f"Nenhum documento encontrado em {CORPUS_DIR}")

    store = FAISS.from_documents(docs, embeddings)
    store.save_local(str(VECTOR_DIR), index_name=settings.vector_index_name)
    return store

def search_documents(query: str, k: int = 3) -> list[dict]:
    store = ensure_vector_store()
    docs = store.similarity_search(query, k=k)
    return [{"content": d.page_content, "metadata": d.metadata} for d in docs]