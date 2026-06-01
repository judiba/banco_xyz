from pathlib import Path
from backend.core.prompt_loader import load_prompt

RAG_PROMPT = load_prompt("rag.md")

# TODO: Refatorar para usar um sistema de templates de prompt mais robusto, que permita a personalização dinâmica dos prompts com base no contexto do usuário, tipo de consulta, ou outros fatores relevantes. O código atual é um exemplo simples de carregamento de um prompt Markdown, mas a ideia é criar uma estrutura mais flexível e adaptável para diferentes casos de uso.
#    Carrega um prompt Markdown a partir da pasta backend/prompts.
def load_prompt(name: str) -> str:
    base = Path(__file__).resolve().parent.parent / "prompts"
    return (base / name).read_text()
