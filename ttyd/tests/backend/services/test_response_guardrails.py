from backend.services.response_guardrails import (
    FALLBACK_RESPONSE,
    apply_guardrails,
)


def test_accepts_valid_analytics_response():
    question = "Qual foi o share do Domingo Legal?"
    answer = (
        "Entendi. Segue um resumo da análise.\n\n"
        "**Destaques**\n- Share médio: 23.5 no horário das 20h\n"
        "- Pico de audiência entre 21:15 e 21:45"
    )
    result = apply_guardrails(question, answer)
    assert result.ok is True
    assert result.content == answer
    assert result.replaced is False


def test_rejects_empty_response():
    result = apply_guardrails("Como está a audiência?", "   ")
    assert result.ok is False
    assert result.content == FALLBACK_RESPONSE
    assert "resposta_muito_curta" in result.issues


def test_rejects_refusal_pattern():
    result = apply_guardrails(
        "Share do jornal",
        "I'm unable to help with that request.",
    )
    assert result.ok is False
    assert "recusa_ou_erro_llm" in result.issues


def test_rejects_irrelevant_short_answer(monkeypatch):
    monkeypatch.setenv("GUARDRAILS_ENABLED", "true")
    from backend.app_config import settings as settings_module

    settings_module.settings.GUARDRAILS_ENABLED = True

    result = apply_guardrails(
        "Qual foi o desempenho do Domingo Legal na audiência?",
        "Sim.",
    )
    assert result.ok is False
    assert "pouca_relevancia" in result.issues[0] or "resposta_muito_curta" in result.issues
