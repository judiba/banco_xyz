"""
Guardrails simples pós-LLM — valida se a resposta do assistente faz sentido.

Heurísticas provisórias (sem modelo extra). Ajustar conforme regras de negócio.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from backend.app_config.settings import settings

MIN_RESPONSE_CHARS = 20
MAX_RESPONSE_CHARS = 32_000

# Recusa / erro típico de LLM (resposta não útil para o produto).
_REFUSAL_PATTERNS = re.compile(
    r"(?i)("
    r"as an ai|i cannot help|i can't help|i'm unable to|"
    r"não posso ajudar|não tenho acesso|não consigo responder|"
    r"desculpe.{0,40}não (posso|consigo)|"
    r"error\s*\d{3}|internal server error"
    r")"
)

# Palavras comuns em perguntas (ignoradas na checagem de relevância).
_STOPWORDS = frozenset(
    {
        "a",
        "o",
        "os",
        "as",
        "de",
        "da",
        "do",
        "das",
        "dos",
        "e",
        "em",
        "no",
        "na",
        "nos",
        "nas",
        "um",
        "uma",
        "uns",
        "umas",
        "que",
        "qual",
        "quais",
        "como",
        "por",
        "para",
        "com",
        "sem",
        "se",
        "me",
        "minha",
        "meu",
        "sua",
        "seu",
        "the",
        "is",
        "are",
        "was",
        "what",
        "how",
        "why",
        "when",
        "where",
    }
)

# Termos que indicam resposta no domínio TTYD / Record (aceita mesmo sem overlap).
_DOMAIN_HINTS = frozenset(
    {
        "audiência",
        "audiencia",
        "share",
        "rating",
        "ibope",
        "programa",
        "grade",
        "horário",
        "horario",
        "praça",
        "praca",
        "record",
        "análise",
        "analise",
        "métrica",
        "metrica",
        "resumo",
        "destaque",
        "sugestão",
        "sugestao",
    }
)

FALLBACK_RESPONSE = (
    "Não consegui validar uma resposta confiável para sua pergunta.\n\n"
    "Tente reformular com mais contexto (programa, horário, praça ou período). "
    "Ex.: *Qual foi o share do Domingo Legal no último domingo?*"
)


@dataclass
class GuardrailResult:
    ok: bool
    content: str
    issues: list[str] = field(default_factory=list)
    replaced: bool = False


def validate_assistant_response(user_question: str, assistant_response: str) -> GuardrailResult:
    """Valida resposta do assistente; retorna texto final (original ou fallback)."""
    if not settings.GUARDRAILS_ENABLED:
        return GuardrailResult(ok=True, content=assistant_response or "")

    text = (assistant_response or "").strip()
    issues: list[str] = []

    if len(text) < MIN_RESPONSE_CHARS:
        issues.append("resposta_muito_curta")
    if len(text) > MAX_RESPONSE_CHARS:
        issues.append("resposta_muito_longa")
    if _REFUSAL_PATTERNS.search(text):
        issues.append("recusa_ou_erro_llm")
    if _is_mostly_repeated(text):
        issues.append("texto_repetitivo")
    if not _seems_relevant(user_question, text):
        issues.append("pouca_relevancia_com_pergunta")

    if issues:
        return GuardrailResult(
            ok=False,
            content=FALLBACK_RESPONSE,
            issues=issues,
            replaced=True,
        )

    return GuardrailResult(ok=True, content=text)


def apply_guardrails(user_question: str, assistant_response: str) -> GuardrailResult:
    """Atalho usado pelo chat após geração do LLM."""
    return validate_assistant_response(user_question, assistant_response)


def _normalize_words(text: str) -> set[str]:
    tokens = re.findall(r"[a-zà-ú0-9]{3,}", text.lower())
    return {t for t in tokens if t not in _STOPWORDS}


def _seems_relevant(user_question: str, response: str) -> bool:
    response_words = _normalize_words(response)
    if response_words & _DOMAIN_HINTS:
        return True

    question_words = _normalize_words(user_question)
    if not question_words:
        return len(response) >= MIN_RESPONSE_CHARS

    overlap = question_words & response_words
    if overlap:
        return True

    # Pergunta longa sem overlap: exige resposta estruturada mínima.
    if len(user_question) > 40:
        return len(response) >= 80 and ("\n" in response or "**" in response or "- " in response)

    return len(response) >= 50


def _is_mostly_repeated(text: str) -> bool:
    words = re.findall(r"[a-zà-ú]{3,}", text.lower())
    if len(words) < 12:
        return False
    counts: dict[str, int] = {}
    for w in words:
        counts[w] = counts.get(w, 0) + 1
        if counts[w] >= 8:
            return True
    return False
