from typing import Any

from backend.agents.runtime.context import AgentContext
from backend.agents.agent import Agent


class Orchestrator:
    def __init__(self):
        self.agent = Agent()

    async def run(self, question: str):
        ctx = AgentContext(question=question)
        return await self.agent.run(ctx)

    async def execute(self, questions: list[str]):
        results = []
        for question in questions:
            result = await self.run(question)
            results.append(result)
        return results

    async def stream(self, question: str):
        ctx = AgentContext(question=question)

        async for token in self.agent.stream(ctx):
            yield token