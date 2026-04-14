from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.core.config import settings

app = FastAPI(
    title="Banco XYZ AI Advisor API",
    version="1.0.0",
    description="API para geração assistida de relatórios de investimentos com LangGraph, RAG e aprovação humana.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")

@app.get("/")
def root() -> dict:
    return {"app": app.title, "env": settings.app_env, "docs": "/docs"}
