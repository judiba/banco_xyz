# backend/agents/runtime/rag_search.py

from backend.rag.search import rag_search_service as core_rag


async def search(ctx):
    return await core_rag(ctx)
