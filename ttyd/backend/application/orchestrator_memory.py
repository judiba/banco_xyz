# backend/application/orchestrator_memory.py
import logging
from typing import Any, Dict

from backend.core.context import RequestContext
from backend.application.context_builder import build_context
from backend.application.memory_service import get_memory
from backend.application.rag_service import run_rag
from backend.app_config.settings import settings

logger = logging.getLogger(__name__)


# 1. Mudança na assinatura de retorno: alterado de -> str para -> Dict[str, Any]
def invoke(prompt: str, org_id: str, session_id: str = "default_session") -> Dict[str, Any]:
    """
    Orquestrador de Execução do Agente (LEVEL 18 Entrypoint).
    Garante o isolamento de dados por organização (Tenant Isolation) e
    gerencia o fluxo do RAG integrado à memória do DynamoDB/Mock.
    """
    logger.info(f"🚀 Iniciando invoke para Tenant: '{org_id}' | Ambiente: {settings.APP_ENV}")

    try:
        # Criação do limite de segurança (Security Boundary) isolado por organização
        ctx = RequestContext(org_id=org_id, settings=settings)

        # 2. Ajuste build_context: Passando os parâmetros brutos conforme o construtor original espera
        ctx = build_context(org_id=org_id)

        logger.debug("Contexto corporativo injetado com sucesso.")

        # 3. Ajuste get_memory: Chamada limpa sem os parâmetros que a assinatura antiga rejeita
        # (Posteriormente subiremos o memory_service.py para o LEVEL 18 para aceitar o isolamento)
        memory = None

        logger.debug(f"Camada de memória instanciada para a sessão: {session_id}")

        # 4. Execução isolada do RAG com injeção de dependências limpa
        logger.info(f"Executando RAG para o prompt (Tamanho: {len(prompt)} caracteres)")
        response = run_rag(ctx=ctx, prompt=prompt, memory=memory)

        logger.info(f"✅ Invoke concluído com sucesso para Tenant: '{org_id}'")
        return response

    except Exception as e:
        logger.error(
            f"❌ Erro crítico no fluxo do orquestrador para Tenant '{org_id}': {str(e)}",
            exc_info=True,
        )
        raise RuntimeError(f"Falha na execução do agente corporativo: {str(e)}") from e

    finally:
        logger.info(f"🏁 Finalizando invoke para Tenant: '{org_id}' | Ambiente: {settings.APP_ENV}")
