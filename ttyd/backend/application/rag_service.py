import json
import logging
from pathlib import Path
from typing import Any, Dict, List

from strands import Agent

from backend.agents.text_to_sql import get_text_to_sql_agent
from backend.app_config.bedrock import get_bedrock_model
from backend.app_config.settings import settings
from backend.prompts.registry import get_prompt
from backend.rag import search as rag_search_module

logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parent.parent
MOCK_DATA_DIR = ROOT / "mock_data"

KEYWORDS_OFFLINE = {
    "finance": ["financeiro", "venda", "kpi", "faturamento", "receita"],
    "channels": ["rag", "canal", "métrica"],
    "users": ["churn", "usuário", "retenção"],
}

def text_to_sql_tool(question: str) -> str:
    agent = get_text_to_sql_agent()
    return str(agent(question))

def build_rag_agent(memory_history: Any = None) -> Agent:
    logger.info("Construindo instância dinâmica do RAG Agent...")

    system_prompt = (
        f"{get_prompt('rag')}\n"
        f"Prompts de Segurança: {get_prompt('guardrails')}\n"
        "Você tem acesso a duas ferramentas corporativas fundamentais:\n"
        "- rag_search_tool: busca documentos institucionais.\n"
        "- text_to_sql_tool: executa queries estruturadas no Redshift.\n"
        "Escolha a melhor ferramenta com base na dúvida do usuário."
    )

    return Agent(
        model=get_bedrock_model(),
        system_prompt=system_prompt,
        tools=[rag_search_module.rag_search_tool, text_to_sql_tool],
        conversation_manager=memory_history,
    )


def load_mock_data(filename: str) -> List[Dict[str, Any]]:
    path = MOCK_DATA_DIR / filename
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception as e:
            logger.error("Erro ao ler arquivo de mock %s: %s", filename, e)
    return []


def run_rag(ctx: Any, prompt: str, memory: Any) -> Dict[str, Any]:
    prompt_lower = prompt.lower()

    if settings.DEV_OFFLINE:
        logger.info("RAG acionado em modo DEV_OFFLINE")

        category = "documents"
        mock_file = "docs.json"
        text_response = (
            "Como assistente offline, localizei documentos relevantes na base institucional."
        )

        if any(w in prompt_lower for w in KEYWORDS_OFFLINE["finance"]):
            category = "sales"
            mock_file = "mock_sales.json"
            data = load_mock_data(mock_file)
            val = data[0].get("receita") if data else "N/A"
            text_response = (
                "Análise de Vendas (Mock): Identificamos que a receita mais recente "
                f"mapeada foi de {val}."
            )

        elif any(w in prompt_lower for w in KEYWORDS_OFFLINE["channels"]):
            category = "metrics"
            mock_file = "mock_metrics.json"
            data = load_mock_data(mock_file)
            canal = data[0].get("canal") if data else "N/A"
            text_response = (
                "Métricas de Canais (Mock): O canal com maior destaque identificado "
                f"no arquivo local foi {canal}."
            )

        elif any(w in prompt_lower for w in KEYWORDS_OFFLINE["users"]):
            category = "users"
            mock_file = "mock_users.json"
            data = load_mock_data(mock_file)
            churn = data[0].get("churn") if data else "N/A"
            text_response = (
                f"Análise de Churn (Mock): A taxa registrada localmente aponta para {churn}."
            )

        return {
            "type": "text",
            "from": "[MOCK LLM - DEV_OFFLINE]",
            "text": text_response,
            "prompt": prompt,
            "category": category,
            "org_id": getattr(ctx, "org_id", "unknown"),
            "mock_data": load_mock_data(mock_file)[:1],
        }

    logger.info("RAG acionado em modo real. Env: %s", settings.APP_ENV)

    try:
        session_id = "default_session"

        if memory is not None:
            session_id = getattr(memory, "session_id", "default_session")
            historico_messages = memory.carregar(session_id=session_id)
        else:
            historico_messages = []

        agent = build_rag_agent(memory_history=historico_messages)
        result = agent(prompt)

        if memory is not None:
            memory.salvar(
                session_id=session_id,
                user_message=prompt,
                ai_message=str(result),
            )

        return {"type": "text", "text": str(result), "raw": result}

    except Exception as e:
        logger.error("Erro crítico durante execução do RAG real no Bedrock: %s", e, exc_info=True)
        return {
            "type": "error",
            "text": f"O serviço de RAG falhou ao processar a inferência online: {str(e)}",
        }