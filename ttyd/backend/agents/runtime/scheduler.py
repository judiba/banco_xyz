async def run_plan(agent, ctx):
    yield "Analisando pergunta...\n"
    docs = await agent.retrieve(ctx)
    yield "Contexto recuperado...\n"
    async for token in agent.generate(ctx, docs):
        yield token
