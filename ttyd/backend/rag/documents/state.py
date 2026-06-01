from typing import Optional
from backend.infrastructure.rag_docs.store import FaissRAGDocsIndex

_rag_docs_index: Optional[FaissRAGDocsIndex] = None


def get_rag_docs_index() -> FaissRAGDocsIndex:
    """
    Retorna o índice RAG Docs (singleton).
    """
    global _rag_docs_index

    if _rag_docs_index is None:
        _rag_docs_index = FaissRAGDocsIndex()

    return _rag_docs_index
