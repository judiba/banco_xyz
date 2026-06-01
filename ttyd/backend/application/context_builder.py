import numpy as np
from backend.rag.sql.state import get_rag_sql_index
from backend.ingestion.embedding import titan_embed
from backend.core.context import RequestContext
from backend.app_config.settings import settings


def build_context(org_id: str):
    return RequestContext(
        org_id=org_id,
        settings=settings,
    )


def rag_context(question: str, top_k: int = 5) -> dict:
    print("entrou na tool rag_context")
    """
    Recupera contexto auxiliar para geração de SQL.
    """
    index = get_rag_sql_index()

    if index.index.ntotal == 0:
        return {"error": "RAG SQL index vazio. Execute o bootstrap."}

    q = titan_embed(question)
    q = q / (np.linalg.norm(q) + 1e-12)

    hits = index.search(q, k=top_k)

    return {
        "question": question,
        "top_k": top_k,
        "context": hits,
    }
