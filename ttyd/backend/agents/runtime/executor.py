import asyncio
from backend.agents.runtime.orchestrator import get_runtime


async def stream_chat(question, session_id=None):
    runtime = get_runtime()

    async for token in runtime.stream(question, session_id):
        yield token


async def run_blocking(func, *args, **kwargs):
    """
    Executa uma função síncrona em uma thread separada para não bloquear o loop de eventos.
    """
    return await asyncio.to_thread(func, *args, **kwargs)
