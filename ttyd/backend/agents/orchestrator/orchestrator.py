# backend/agents/orchestrator/orchestrator.py

from backend.agents.runtime.orchestrator import Orchestrator

__all__ = ["Orchestrator"]


def get_orchestrator():
    return Orchestrator()
