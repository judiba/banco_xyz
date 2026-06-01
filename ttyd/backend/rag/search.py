import logging
from strands import tool
from backend.ingestion.rag_store import get_rag_index

logger = logging.getLogger(__name__)


@tool
def rag_search_tool(question: str, top_k: int = 5):
    """
    Ferramenta principal de busca RAG (Retrieval-Augmented Generation).
    Consulta documentos institucionais da Record TV no índice vetorial.
    """
    index = get_rag_index()

    if index.index.ntotal == 0:
        return {"error": "O índice RAG está vazio ou não foi inicializado."}

    hits = index.search(question, k=top_k)

    return {
        "question": question,
        "results": [
            {
                "text": h["text"],
                "score": h["score"],
                "file_id": h["meta"].get("file_id", "unknown"),
            }
            for h in hits
        ],
    }


async def rag_search_service(ctx):
    """
    Wrapper assíncrono para o Runtime utilizar a ferramenta de busca RAG.
    Extrai o contexto e retorna apenas o conteúdo textual para o LLM.
    """
    question = getattr(ctx, "question", None) or str(ctx)
    results = rag_search_tool(question=question)

    if isinstance(results, dict):
        docs = results.get("results", [])

        return [r.get("text", "") for r in docs if isinstance(r, dict) and "text" in r]

    if isinstance(results, dict) and "error" in results:
        return [results["error"]]

    return []
