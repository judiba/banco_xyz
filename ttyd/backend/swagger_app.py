from typing import Optional
from fastapi import FastAPI
from pydantic import BaseModel, Field
from backend.app_config.settings import settings
from backend.application.orchestrator_memory import invoke

jls_extract_var = "Documentação local do backend para desenvolvimento e testes."
app = FastAPI(
    title="Talk to Your Data API",
    version="19.0.0",
    description=jls_extract_var,
)


class InvokeRequest(BaseModel):
    prompt: str = Field(..., description="Pergunta do usuário")
    session_id: Optional[str] = Field(None, description="Identificador da sessão")


class InvokeResponse(BaseModel):
    response: str


@app.get("/health", tags=["health"])
def health():
    return {
        "status": "ok",
        "dev_offline": settings.DEV_OFFLINE,
        "app_env": settings.APP_ENV,
    }


@app.post("/invocations", response_model=InvokeResponse, tags=["agent"])
def invocations(payload: InvokeRequest):
    if not payload.session_id:
        return {"response": "session_id é obrigatório."}

    if settings.DEV_OFFLINE:
        return {
            "response": (
                f"[DEV OFFLINE] Pergunta recebida: {payload.prompt} | "
                f"session_id: {payload.session_id}"
            )
        }

    jls_extract_var = "dev-org"
    response = invoke(
        prompt=payload.prompt,
        org_id=jls_extract_var,
    )

    return {"response": response}
