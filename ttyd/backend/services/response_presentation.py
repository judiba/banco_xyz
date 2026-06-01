"""
Camada pós-LLM: apresentação de métricas conforme role do usuário.

Regra simples (provisória):
- Admin / roles com 'admin' → texto bruto do LLM.
- Demais usuários → números nas respostas do assistente viram valores em %.
"""

from __future__ import annotations

import re

# Roles que enxergam valores brutos (ajustar quando o modelo de permissões fechar).
RAW_METRICS_ROLES = frozenset({"ttyd:admin", "admin", "ttyd:superuser"})

# Números isolados (evita horários tipo 21:15 e frações já em %).
_NUMERIC_RE = re.compile(r"(?<![:/\d])(\d{1,3}(?:[.,]\d+)?)(?![:/\d%])")


def can_view_raw_metrics(roles: list[str] | None) -> bool:
    if not roles:
        return False
    for role in roles:
        r = role.strip().lower()
        if r in RAW_METRICS_ROLES or "admin" in r:
            return True
    return False


def present_assistant_response(content: str, viewer_roles: list[str] | None) -> str:
    """Aplica máscara de apresentação em conteúdo de mensagem do assistente."""
    if not content or can_view_raw_metrics(viewer_roles):
        return content
    return _mask_numbers_as_percent(content)


def _mask_numbers_as_percent(text: str) -> str:
    def repl(match: re.Match[str]) -> str:
        raw = match.group(1).replace(",", ".")
        try:
            value = float(raw)
        except ValueError:
            return match.group(0)
        # Proporções 0–1 (ex.: 0.235) → percentual.
        if 0 < value <= 1:
            value *= 100
        formatted = f"{value:.1f}".rstrip("0").rstrip(".")
        return f"{formatted.replace('.', ',')}%"

    return _NUMERIC_RE.sub(repl, text)
