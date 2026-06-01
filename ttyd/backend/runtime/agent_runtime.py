import asyncio
from backend.agents.agentcore_runtime import AgentCoreRuntime
from backend.agents.agent_orchestrator import get_orchestrator
from backend.application.context_builder import build_context
from backend.infrastructure.vector_store import vector_store


async def run_agent_core():
    # Obter o agente principal
    agent = get_orchestrator()

    # Construir o contexto
    context = build_context()

    # Inicializar o runtime do agente
    runtime = AgentCoreRuntime(agent, context, vector_store)

    # Executar o agente
    await runtime.run()


asyncio.run(run_agent_core())
