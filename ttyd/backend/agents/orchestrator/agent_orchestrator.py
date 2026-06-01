# backend/agents/orchestrator/orchestrator.py

from .agent_orchestrator import Orchestrator

__all__ = ["get_orchestrator"]

_orchestrator = None


def get_orchestrator():
    global _orchestrator

    if _orchestrator is None:
        _orchestrator = Orchestrator()

    return _orchestrator
