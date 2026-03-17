from langchain.agents import create_agent

from app.model import get_model
from app.memory import get_memory

from app.tools.bible_api import bible_lookup
from app.tools.http_tools import http_get


def build_agent():

    model = get_model()

    memory = get_memory()

    agent = create_agent(
        model=model,
        tools=[bible_lookup, http_get],
        memory=memory,
        system_prompt="""
Você é um assistente avançado com acesso a múltiplas APIs.

Ferramentas disponíveis:

bible_lookup -> buscar versículos da bíblia
http_get -> acessar qualquer API pública

Use ferramentas quando necessário para responder.
"""
    )

    return agent