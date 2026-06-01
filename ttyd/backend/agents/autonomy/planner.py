from backend.agents.runtime.agent import Agent
from backend.agents.runtime.context import AgentContext


async def plan():
    agent = Agent()
    ctx = AgentContext(question="Improve system performance")
    return await agent.run(ctx)
