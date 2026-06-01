# backend/agents/runtime/rag_search.py

from backend.rag.rag_search import rag_search as core_rag


async def search(ctx):
    return await core_rag(ctx)
