from collections.abc import AsyncIterator

from backend.agents.runtime.context import AgentContext


class Agent:
    def __init__(self):
        self.system_prompt = "orchestrator"

    async def retrieve(self, ctx: AgentContext):
        try:
            from backend.rag.rag_search import rag_search
            return await rag_search(ctx)
        except Exception:
            return []

    async def generate(self, ctx: AgentContext, docs) -> AsyncIterator[str]:
        yield "Processando pergunta...\n"
        if docs:
            yield "Contexto recuperado.\n"
        yield f"Pergunta recebida: {ctx.question}\n"

    async def stream(self, ctx: AgentContext) -> AsyncIterator[str]:
        docs = await self.retrieve(ctx)
        async for token in self.generate(ctx, docs):
            yield token

    async def run(self, ctx: AgentContext) -> str:
        response = ""
        async for token in self.stream(ctx):
            response += token
        return response
