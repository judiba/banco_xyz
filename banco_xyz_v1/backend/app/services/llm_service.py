from __future__ import annotations

from typing import Optional, List
import hashlib
import math

from app.core.config import settings

try:
    from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
except Exception:  # pragma: no cover
    AzureChatOpenAI = None
    AzureOpenAIEmbeddings = None

from langchain_core.embeddings import Embeddings

SYSTEM_PROMPT = (
    "Você é um assessor de investimentos do Banco XYZ. "
    "Escreva em português do Brasil, com clareza, tom consultivo e sem prometer retorno. "
    "Use o contexto do cliente, aderência ao perfil, horizonte, objetivo, evento recente, "
    "benchmarks externos e os trechos do RAG. "
    "Quando solicitado, gere duas versões do relatório: uma resumida e outra detalhada, "
    "com comparação de benchmarks e recomendações compatíveis com o perfil do investidor."
)

class LocalHashEmbeddings(Embeddings):
    def __init__(self, dim: int = 256):
        self.dim = dim

    def _embed(self, text: str) -> List[float]:
        vec = [0.0] * self.dim
        tokens = (text or "").lower().split()
        for token in tokens:
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            idx = int.from_bytes(digest[:4], "big") % self.dim
            sign = 1.0 if digest[4] % 2 == 0 else -1.0
            vec[idx] += sign
        norm = math.sqrt(sum(v * v for v in vec)) or 1.0
        return [v / norm for v in vec]

    def embed_query(self, text: str) -> List[float]:
        return self._embed(text)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return [self._embed(text) for text in texts]


def get_chat_model() -> Optional[object]:
    if not all([
        settings.azure_openai_api_key,
        settings.azure_openai_endpoint,
        settings.azure_openai_chat_deployment,
        AzureChatOpenAI,
    ]):
        return None
    return AzureChatOpenAI(
        api_key=settings.azure_openai_api_key,
        azure_endpoint=settings.azure_openai_endpoint,
        api_version=settings.azure_openai_api_version,
        azure_deployment=settings.azure_openai_chat_deployment,
        temperature=0.2,
    )


def get_embeddings() -> Embeddings:
    if all([
        settings.azure_openai_api_key,
        settings.azure_openai_endpoint,
        settings.azure_openai_embeddings_deployment,
        AzureOpenAIEmbeddings,
    ]):
        return AzureOpenAIEmbeddings(
            api_key=settings.azure_openai_api_key,
            azure_endpoint=settings.azure_openai_endpoint,
            api_version=settings.azure_openai_api_version,
            azure_deployment=settings.azure_openai_embeddings_deployment,
        )
    return LocalHashEmbeddings(dim=256)


def generate_text(prompt: str, fallback_summary: str) -> str:
    llm = get_chat_model()
    if llm is None:
        return fallback_summary
    response = llm.invoke([
        ("system", SYSTEM_PROMPT),
        ("human", prompt),
    ])
    return response.content
