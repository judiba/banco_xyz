from backend.prompts.registry import get_prompt
from backend.rag.rag_search import rag_search


class Agent:
    def __init__(self, llm):
        self.llm = llm
        self.system_prompt = get_prompt("orchestrator")

    # ------------------------------------------------
    # STREAM RESPONSE (LEVEL 17 CORE)
    # ------------------------------------------------
    async def stream(self, ctx):
        # 1️⃣ Buscar contexto RAG
        docs = await rag_search(ctx)

        # 2️⃣ Construir prompt final
        final_prompt = self._build_prompt(ctx, docs)

        # 3️⃣ Streaming do LLM
        async for token in self.llm.stream(
            system_prompt=self.system_prompt,
            user_input=final_prompt,
        ):
            yield token

    # ------------------------------------------------
    # PROMPT BUILDER
    # ------------------------------------------------
    def _build_prompt(self, ctx, docs):
        context_text = "\n".join(docs)

        return f"""
Context:
{context_text}

User Question:
{ctx.question}
"""
