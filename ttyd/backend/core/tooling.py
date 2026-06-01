from backend.core.prompt_loader import load_prompt


def tool(func=None, **kwargs):
    def wrap(f):
        return f

    return wrap if func is None else wrap(func)


RAG_PROMPT = load_prompt("rag.md")
