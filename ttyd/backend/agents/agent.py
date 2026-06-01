"""Compatibility shim for older imports.

Prefer: from backend.agents.runtime.agent import Agent
"""

from backend.agents.runtime.agent import Agent
from backend.agents.runtime.context import AgentContext


async def run(question: str, org: str | None = None):
    context = AgentContext(question=question, metadata={"org": org} if org else {})
    agent = Agent()
    full_response = ""
    async for token in agent.stream(context):
        full_response += token
    return full_response


__all__ = ["Agent", "AgentContext", "run"]
