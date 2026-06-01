import faiss

# third party optional
try:
    from backend.rag.search import real_search
except ImportError:

    def real_search(*args, **kwargs):
        return []


from strands import tool

# internos
from backend.core.storage import tenant_path
from backend.infrastructure.rds.docs_state import get_rag_docs_index


def load_index(context):
    index_path = tenant_path(context.namespace) / "faiss.index"

    return faiss.read_index(str(index_path))


@tool
def rag_search(question: str, top_k: int = 5):
    print("entrou na tool rag_search")
    index = get_rag_docs_index()

    if index.index.ntotal == 0:
        return {"error": "Índice RAG Docs vazio. Faça o bootstrap primeiro."}

    hits = index.search(question, k=top_k)

    return {
        "question": question,
        "results": [
            {
                "text": h["text"],
                "score": h["score"],
                "file_id": h["meta"]["file_id"],
            }
            for h in hits
        ],
    }
