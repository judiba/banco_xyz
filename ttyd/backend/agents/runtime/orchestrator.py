from collections.abc import AsyncIterator

from backend.agents.runtime.agent import Agent
from backend.agents.runtime.context import AgentContext
from backend.agents.runtime.scheduler import run_plan


class RuntimeOrchestrator:
    def __init__(self):
        self.agent = Agent()

    async def stream(self, question: str, session_id: str | None = None) -> AsyncIterator[str]:
        ctx = AgentContext(question=question, session_id=session_id)
        async for token in run_plan(self.agent, ctx):
            yield token

    async def run(self, question: str, session_id: str | None = None) -> str:
        ctx = AgentContext(question=question, session_id=session_id)
        return await self.agent.run(ctx)


_runtime = RuntimeOrchestrator()


def get_runtime() -> RuntimeOrchestrator:
    return _runtime
