# backend/agents/runtime/rag_async.py

from backend.rag.search import rag_search_service as rag_search


async def retrieve_context(ctx):
    docs = await rag_search(ctx)

    ctx.update("docs", docs)

    return docs
