import asyncio

from backend.agents.agentcore_runtime import AgentCoreRuntime
from backend.agents.agent_orchestrator import get_orchestrator
from backend.application.context_builder import build_context
from backend.infrastructure.vector_store import vector_store


async def start_runtime():
    agent = get_orchestrator()
    context = build_context()

    runtime = AgentCoreRuntime(
        agent=agent,
        context=context,
        vector_store=vector_store,
    )

    await runtime.run()


def run():
    asyncio.run(start_runtime())
