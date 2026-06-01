# backend/application/memory_service.py
import logging
from typing import Any, List, Dict

from backend.app_config.settings import settings
from backend.app_config.gerenciador_memoria import GerenciadorMemoria

logger = logging.getLogger(__name__)


# ============================================================================
# APENAS SE FOR USAR O MOCK DE INFERÊNCIA DO SUMARIZADOR (DEIXADO DE FORMA LIMPA)
# ============================================================================
def summarize_messages(messages: List[Any]) -> str:
    """Implementa a lógica de resumo corporativo para compressão de histórico."""
    if not messages:
        return ""

    text_block = ""
    for m in messages:
        # Verifica se o objeto possui o tipo/conteúdo esperado do LangChain
        content = getattr(m, "content", str(m))
        role = getattr(m, "type", "user")
        text_block += f"{role}: {content}\n"

    logger.debug(f"Sumarizando bloco de mensagens (Tamanho: {len(text_block)})")
    return "Resumo da conversa anterior estruturado."


# ============================================================================
# SERVIÇO DE MEMÓRIA CORPORATIVA (LEVEL 18)
# ============================================================================
def get_memory(org_id: str = "default", session_id: str = "default_session") -> GerenciadorMemoria:
    """
    Fábrica gerenciadora que instancia o ciclo de vida do GerenciadorMemoria.
    Injeta o nome da tabela mapeado diretamente pelas configurações globais do ambiente.
    """
    # Lê dinamicamente do settings corrigido (.env, .env.local ou Terraform)
    nome_tabela = settings.DYNAMODB_TABLE_PREFIX + "-messages"

    logger.debug(
        f"Instanciando GerenciadorMemoria para o Tenant '{org_id}' na tabela '{nome_tabela}'"
    )
    return GerenciadorMemoria(db_table_name=nome_tabela)


def format_message(role: str, text: str) -> Dict[str, Any]:
    """Formata mensagens no padrão aceito pela camada de persistência."""
    return {"role": role, "content": [{"text": text}]}


def execute_memory_cycle(user_input: str, session_id: str, org_id: str) -> str:
    """
    Orquestra o ciclo local de leitura, salvamento e resposta da memória.
    Substitui a função procedimental e comentada antiga ('invoke_orchestrator').
    """
    logger.info(f"Processando ciclo de memória para a sessão: {session_id} | Tenant: {org_id}")

    # 1. Obtém a instância limpa do gerenciador multi-ambiente
    memory = get_memory(org_id=org_id, session_id=session_id)

    # Simulação da resposta do agente (Substitua pela chamada real do seu orquestrador se necessário)
    response_text = "Resposta do assistente (Consistente)"

    # 2. Uso correto de memory.salvar condizente com a classe GerenciadorMemoria
    try:
        memory.salvar(
            session_id=session_id,
            user_message=user_input,
            ai_message=response_text,
        )
        logger.debug(f"Mensagem da sessão {session_id} persistida com sucesso.")
    except Exception as e:
        logger.error(f"Falha ao persistir ciclo de memória: {e}")

    return response_text
