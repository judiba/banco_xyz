from dataclasses import dataclass, field
from typing import Any


@dataclass
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


class SessionManager:
    def __init__(self):
        self.sessions = {}  # conversation_id -> AgentContext

    def get_session(self, conversation_id: str, create_if_not_exists=True):
        if conversation_id in self.sessions:
            return self.sessions[conversation_id]

        if create_if_not_exists:
            session = AgentContext(conversation_id=conversation_id)
            self.sessions[conversation_id] = session
            return session

        return None

    def clear_session(self, conversation_id: str):
        if conversation_id in self.sessions:
            del self.sessions[conversation_id]
