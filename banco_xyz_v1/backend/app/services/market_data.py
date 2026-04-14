from __future__ import annotations

from typing import Dict, List


def build_market_snapshot() -> Dict[str, float]:
    return {
        "cdi_12m": 10.90,
        "ibovespa_12m": 13.40,
        "ifix_12m": 7.20,
        "ima_b_12m": 9.10,
        "usd_brl": 5.12,
    }


def recommend_allocation(client: dict) -> List[dict]:
    profile = (client.get("perfil_suitability") or "Conservador").strip()
    allocations = {
        "Conservador": [
            {"classe": "Tesouro Selic e caixa", "peso": 35},
            {"classe": "CDB/LCI/LCA high grade", "peso": 30},
            {"classe": "Renda fixa IPCA", "peso": 20},
            {"classe": "Multimercado baixa volatilidade", "peso": 10},
            {"classe": "Fundos imobiliários", "peso": 5},
        ],
        "Moderado": [
            {"classe": "Renda fixa pós e IPCA", "peso": 35},
            {"classe": "Multimercado", "peso": 20},
            {"classe": "Fundos imobiliários", "peso": 15},
            {"classe": "Ações Brasil", "peso": 15},
            {"classe": "Internacional", "peso": 15},
        ],
        "Arrojado": [
            {"classe": "Ações Brasil", "peso": 30},
            {"classe": "Internacional", "peso": 20},
            {"classe": "Fundos multimercado", "peso": 20},
            {"classe": "Fundos imobiliários", "peso": 10},
            {"classe": "Renda fixa oportunística", "peso": 20},
        ],
    }
    return allocations.get(profile, allocations["Conservador"])
