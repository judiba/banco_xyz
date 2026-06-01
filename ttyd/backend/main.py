from fastapi import FastAPI, Response
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from starlette.exceptions import HTTPException as StarletteHTTPException


from backend.api.v1.errors import (
    ApiException,
    api_exception_handler,
    http_exception_handler,
    validation_exception_handler,
)
from backend.api.v1.router import api_v1_router
from backend.api.v1.routes import saml as saml_routes
from backend.app_config.logging import setup_logging, CorrelationIdMiddleware

# Inicialização global do logger corporativo e tracing (LEVEL 19)
setup_logging()

app = FastAPI(
    title="Talk to Your Data API",
    version="19.0.0",
    description="API principal (v1) + rotas legadas de chat/invoke.",
)

# Registra o middleware de correlation ID e latência de processamento
app.add_middleware(CorrelationIdMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(ApiException, api_exception_handler)  # type: ignore[arg-type]
app.add_exception_handler(StarletteHTTPException, http_exception_handler)  # type: ignore[arg-type]
app.add_exception_handler(RequestValidationError, validation_exception_handler)  # type: ignore[arg-type]


app.include_router(api_v1_router)
# Compatibilidade ContentAI / Record: /api/auth/saml/* (mesmos handlers de /v1/auth/saml/*)
app.include_router(saml_routes.router, prefix="/api")


class InvokeRequest(BaseModel):
    question: str


@app.get("/")
def root():
    return {
        "status": "ok",
        "service": "TTYD Backend",
        "docs": "/docs",
        "api_v1": "/v1",
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return Response(status_code=204)


@app.post("/invoke")
async def run(payload: InvokeRequest):
    from backend.app_config.settings import settings

    if settings.DEV_OFFLINE:
        return {"answer": (f"[DEV OFFLINE] Resposta simulada para: {payload.question}")}

    from backend.application.orchestrator_memory import invoke

    response = invoke(
        prompt=payload.question,
        org_id="dev-org",
    )
    answer = response.get("text", response) if isinstance(response, dict) else response
    return {"answer": answer}
