from __future__ import annotations

from datetime import date, timedelta
from typing import Any

import requests

BRAPI_BASE_URL = "https://brapi.dev/api"
BRASIL_API_BASE_URL = "https://brasilapi.com.br/api"
BCB_BASE_URL = "https://api.bcb.gov.br/dados/serie"

DEFAULT_TIMEOUT = 20

# Códigos SGS comuns do BCB
# 432 = Selic meta diária
# 12 = CDI diário
# 433 = IPCA mensal
BCB_SERIES = {
    "selic": 432,
    "cdi": 12,
    "ipca": 433,
}


def _safe_get_json(url: str, **kwargs: Any) -> Any:
    response = requests.get(url, timeout=DEFAULT_TIMEOUT, **kwargs)
    response.raise_for_status()
    return response.json()


def get_current_rates() -> dict[str, float | None]:
    """
    Usa Brasil API para taxas correntes.
    Espera itens com nome/valor, como Selic, CDI e IPCA.
    """
    try:
        data = _safe_get_json(f"{BRASIL_API_BASE_URL}/taxas/v1")
    except Exception:
        return {"selic": None, "cdi": None, "ipca": None}

    result = {"selic": None, "cdi": None, "ipca": None}

    for item in data:
        nome = str(item.get("nome", "")).strip().lower()
        valor = item.get("valor")
        if nome == "selic":
            result["selic"] = valor
        elif nome == "cdi":
            result["cdi"] = valor
        elif nome == "ipca":
            result["ipca"] = valor

    return result


def get_bcb_series(
    series_code: int,
    start: date,
    end: date,
) -> list[dict[str, Any]]:
    data_inicial = start.strftime("%d/%m/%Y")
    data_final = end.strftime("%d/%m/%Y")

    url = (
        f"{BCB_BASE_URL}/bcdata.sgs.{series_code}/dados"
        f"?formato=json&dataInicial={data_inicial}&dataFinal={data_final}"
    )
    data = _safe_get_json(url)

    normalized: list[dict[str, Any]] = []
    for row in data:
        normalized.append(
            {
                "date": row.get("data"),
                "value": _to_float(row.get("valor")),
            }
        )
    return normalized


def get_bcb_macro_history(days: int = 365) -> dict[str, list[dict[str, Any]]]:
    end = date.today()
    start = end - timedelta(days=days)

    result: dict[str, list[dict[str, Any]]] = {}
    for name, code in BCB_SERIES.items():
        try:
            result[name] = get_bcb_series(code, start, end)
        except Exception:
            result[name] = []
    return result


def get_ibov_history(range_period: str = "1y", interval: str = "1d") -> list[dict[str, Any]]:
    """
    Histórico do Ibovespa via brapi.
    """
    try:
        data = _safe_get_json(
            f"{BRAPI_BASE_URL}/quote/%5EBVSP",
            params={"range": range_period, "interval": interval},
        )
    except Exception:
        return []

    results = data.get("results", [])
    if not results:
        return []

    historical = results[0].get("historicalDataPrice", []) or []
    normalized: list[dict[str, Any]] = []

    for row in historical:
        normalized.append(
            {
                "date": row.get("date"),
                "close": _to_float(row.get("close")),
            }
        )

    return normalized


def get_asset_history(symbol: str, range_period: str = "1y", interval: str = "1d") -> list[dict[str, Any]]:
    """
    Histórico de ativo B3 via brapi.
    Exemplos: PETR4, VALE3, BOVA11, MXRF11
    """
    try:
        data = _safe_get_json(
            f"{BRAPI_BASE_URL}/quote/{symbol}",
            params={"range": range_period, "interval": interval},
        )
    except Exception:
        return []

    results = data.get("results", [])
    if not results:
        return []

    historical = results[0].get("historicalDataPrice", []) or []
    normalized: list[dict[str, Any]] = []

    for row in historical:
        normalized.append(
            {
                "date": row.get("date"),
                "close": _to_float(row.get("close")),
            }
        )

    return normalized


def build_portfolio_vs_benchmarks(
    profile: str,
    portfolio_series: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """
    Gera payload para frontend.
    portfolio_series opcional:
    [
      {"date": "2026-01-01", "portfolio": 100.0},
      ...
    ]
    """
    rates = get_current_rates()
    ibov = get_ibov_history()
    macro = get_bcb_macro_history()

    comparison = {
        "profile": profile,
        "current_rates": rates,
        "ibov_history": ibov,
        "macro_history": macro,
        "portfolio_history": portfolio_series or [],
    }

    return comparison


def build_profile_chart_recommendation(profile: str) -> dict[str, str]:
    profile_normalized = str(profile).strip().lower()

    if "conserv" in profile_normalized:
        return {
            "focus": "Segurança, estabilidade e predominância de renda fixa.",
            "main_chart": "area",
            "secondary_chart": "allocation_bar",
            "benchmarks": "CDI, Selic, IPCA",
        }

    if "moder" in profile_normalized:
        return {
            "focus": "Equilíbrio entre preservação e crescimento.",
            "main_chart": "line_comparison",
            "secondary_chart": "allocation_bar",
            "benchmarks": "Carteira, CDI e Ibovespa",
        }

    return {
        "focus": "Performance, bolsa e maior volatilidade.",
        "main_chart": "line_comparison",
        "secondary_chart": "risk_return_proxy",
        "benchmarks": "Carteira, Ibovespa e ativos da carteira",
    }


def _to_float(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)

    text = str(value).strip().replace(".", "").replace(",", ".")
    try:
        return float(text)
    except ValueError:
        return None