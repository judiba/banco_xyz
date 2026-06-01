"""Compatibility shim for older imports.

Prefer: from backend.agents.runtime.context import AgentContext
"""

from backend.agents.runtime.context import AgentContext

__all__ = ["AgentContext"]
