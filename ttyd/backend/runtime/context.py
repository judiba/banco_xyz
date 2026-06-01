from pydantic import BaseModel
from typing import Optional, Dict, Any

class AgentContext(BaseModel):
    """Contexto de execução para os agentes do TTYD."""
    question: str
    session_id: Optional[str] = "default"
    org_id: Optional[str] = "record-tv"
    metadata: Dict[str, Any] = {}
