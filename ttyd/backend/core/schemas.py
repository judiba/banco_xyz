from pydantic import BaseModel
from typing import Literal, Optional


class ChatRequest(BaseModel):
    org_id: str
    dataset: str = "default"
    chat_id: Optional[str] = None
    query_type: Literal["rag", "chat", "hybrid"] = "hybrid"
    message: str
    session_id: Optional[str] = None
    chat_mode: Literal["proactive", "reactive"] = "reactive"
    context: Optional[dict] = None
    file_name: Optional[str] = None
    chat_topic: Optional[str] = None
