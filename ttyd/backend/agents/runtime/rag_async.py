# backend/agents/runtime/rag_async.py

from backend.rag.rag_search import rag_search


async def retrieve_context(ctx):
    docs = await rag_search(ctx)

    ctx.update("docs", docs)

    return docs
