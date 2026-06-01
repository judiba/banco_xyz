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
