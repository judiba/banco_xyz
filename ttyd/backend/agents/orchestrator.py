"""Compatibility shim for older imports.

Prefer: from backend.agents.runtime.orchestrator import get_runtime
"""

from backend.agents.runtime.orchestrator import RuntimeOrchestrator, get_runtime


def get_orchestrator():
    return get_runtime()


__all__ = ["RuntimeOrchestrator", "get_runtime", "get_orchestrator"]
