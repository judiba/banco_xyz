from typing import Optional
from backend.rag.sql.store import FaissRAGSQLIndex

_rag_sql_index: Optional[FaissRAGSQLIndex] = None

EMBEDDING_DIM = 1536


def get_rag_sql_index() -> FaissRAGSQLIndex:
    """
    Retorna o índice RAG SQL (singleton).
    """
    global _rag_sql_index

    if _rag_sql_index is None:
        _rag_sql_index = FaissRAGSQLIndex(dim=EMBEDDING_DIM)

    return _rag_sql_index
