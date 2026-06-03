"""Compatibility shim for older imports.

Prefer: from backend.agents.runtime.context import AgentContext
"""

from typing import Any
from backend.agents.runtime.context import AgentContext


def get_context():
    """
    Returns a new AgentContext instance.

    Returns:
        AgentContext: The agent context
    """
    return AgentContext()


__all__ = ["AgentContext", "get_context"]


class AgentContext:
    def __init__(
        self,
        question: str,
        user_id: str | None = None,
        conversation_id: str | None = None,
        session_id: str | None = None,
        memory: dict[str, Any] = None,
        documents: list[str] = None,
        metadata: dict[str, Any] = None,
    ):
        self.question = question
        self.user_id = user_id
        self.conversation_id = conversation_id
        self.session_id = session_id
        self.memory = memory or {}
        self.documents = documents or []
        self.metadata = metadata or {}
    
    def update(self, key: str, value: Any) -> None:
        self.metadata[key] = value


class AgentContext:
    question: str
    user_id: str | None = None
    conversation_id: str | None = None
    session_id: str | None = None
    memory: dict[str, Any] = field(default_factory=dict)
    documents: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def update(self, key: str, value: Any) -> None:
        self.metadata[key] = value