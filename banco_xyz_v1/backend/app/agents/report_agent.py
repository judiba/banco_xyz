from __future__ import annotations

import logging
from app.agents.message_agent import build_contact_messages
from datetime import datetime, timezone
from pprint import pformat
from textwrap import dedent
from typing import Any, Dict, Dict
from uuid import uuid4

from app.services.client_repository import get_client
from app.services.llm_service import generate_text
from app.services.market_data import build_market_snapshot, recommend_allocation
from app.services.rag_service import search_documents

from app.services.benchmark_service import (
    build_portfolio_vs_benchmarks,
    build_profile_chart_recommendation,
)

logger: logging.Logger = logging.getLogger(__name__)


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _extract_source(item: Any) -> str | None:
    if not isinstance(item, dict):
        return None

    metadata = item.get("metadata") or {}
    if not isinstance(metadata, dict):
        metadata = {}

    source = (
        item.get("source")
        or metadata.get("source")
        or item.get("file_name")
        or item.get("document_name")
        or item.get("filename")
        or item.get("name")
        or metadata.get("file_name")
        or metadata.get("document_name")
        or metadata.get("filename")
        or metadata.get("name")
    )

    if source is None:
        return None

    return str(source)


def _extract_content(item: Any) -> str:
    if not isinstance(item, dict):
        return str(item)

    metadata = item.get("metadata") or {}
    if not isinstance(metadata, dict):
        metadata = {}

    content = (
        item.get("content")
        or item.get("page_content")
        or item.get("text")
        or item.get("document")
        or metadata.get("content")
        or metadata.get("text")
        or ""
    )

    return str(content).strip()


def _normalize_rag_results(rag_results: Any) -> list[dict]:
    if rag_results is None:
        logger.warning("search_documents retornou None; usando lista vazia")
        return []

    if not isinstance(rag_results, list):
        logger.warning(
            "search_documents retornou tipo inesperado (%s); normalizando para lista",
            type(rag_results).__name__,
        )
        rag_results = [rag_results]

    normalized: list[dict] = []

    for idx, item in enumerate(rag_results):
        logger.debug("RAG item %s bruto: %s", idx, pformat(item))

        if isinstance(item, dict):
            normalized_item = {
                **item,
                "source": _extract_source(item),
                "content": _extract_content(item),
            }
        else:
            normalized_item = {
                "source": None,
                "content": str(item),
                "raw": item,
            }

        normalized.append(normalized_item)

    return normalized


def load_client(state: dict) -> dict:
    client = get_client(state["client_id"])
    audit = state.get("audit_log", []) + [
        {
            "step": "load_client",
            "at": utc_now_iso(),
            "client_id": client["id_pessoa"],
        }
    ]
    return {
        **state,
        "client": client,
        "run_id": state.get("run_id", str(uuid4())),
        "audit_log": audit,
    }


def retrieve_knowledge(state: dict) -> dict:
    client = state["client"]
    query: str = (
        f"perfil {client['perfil_suitability']} objetivo {client['objetivo_investimento']} "
        f"horizonte {client['horizonte_tempo']} tolerancia {client['tolerancia_risco']}"
    )

    logger.info("Iniciando retrieve_knowledge")
    logger.debug("Query RAG: %s", query)

    try:
        rag_results_raw = search_documents(query)
        logger.debug("rag_results_raw tipo=%s", type(rag_results_raw).__name__)
        logger.debug("rag_results_raw valor=%s", pformat(rag_results_raw))

        rag_results = _normalize_rag_results(rag_results_raw)
        snapshot: Dict[str, float] = build_market_snapshot()
        allocation = recommend_allocation(client)

        rag_sources = [item["source"] for item in rag_results if item.get("source")]

        for idx, item in enumerate(rag_results):
            if not item.get("source"):
                logger.warning(
                    "RAG item %s sem source identificável. Chaves=%s",
                    idx,
                    list(item.keys()),
                )
            if not item.get("content"):
                logger.warning("RAG item %s sem content utilizável.", idx)

        audit = state.get("audit_log", []) + [
            {
                "step": "retrieve_knowledge",
                "at": utc_now_iso(),
                "rag_query": query,
                "rag_result_count": len(rag_results),
                "rag_sources": rag_sources,
            }
        ]

        logger.info(
            "retrieve_knowledge finalizado com %s resultados e %s fontes",
            len(rag_results),
            len(rag_sources),
        )

        return {
            **state,
            "rag_results": rag_results,
            "market_snapshot": snapshot,
            "recommended_allocation": allocation,
            "audit_log": audit,
        }

    except Exception as exc:
        logger.exception("Erro em retrieve_knowledge")

        snapshot: Dict[str, float] = build_market_snapshot()
        allocation = recommend_allocation(client)

        audit = state.get("audit_log", []) + [
            {
                "step": "retrieve_knowledge",
                "at": utc_now_iso(),
                "rag_query": query,
                "rag_result_count": 0,
                "rag_sources": [],
                "error": str(exc),
            }
        ]

        return {
            **state,
            "rag_results": [],
            "market_snapshot": snapshot,
            "recommended_allocation": allocation,
            "audit_log": audit,
            "rag_error": str(exc),
        }


def build_prompt(state: dict) -> dict:
    client = state["client"]

    rag_blocks = []
    for idx, item in enumerate(state.get("rag_results", []), start=1):
        source = item.get("source") or f"Fonte RAG {idx}"
        content = item.get("content") or "Conteúdo não disponível."
        rag_blocks.append(f"Fonte: {source}\n{content}")

    rag_context: str = "\n\n".join(rag_blocks)
    if not rag_context:
        rag_context = "Nenhum conhecimento adicional foi recuperado da base RAG."

    allocation_lines: str = "\n".join(
        [f"- {item['classe']}: {item['peso']}%" for item in state["recommended_allocation"]]
    )

    benchmark_block: str = _build_benchmark_block(state)

    prompt: str = dedent(
        f"""
        Gere duas versões do relatório para o cliente abaixo.

        VERSÃO 1 — RESUMIDA
        - até 8 bullets
        - linguagem objetiva
        - diagnóstico da carteira
        - comparação com benchmarks externos
        - 3 recomendações práticas

        VERSÃO 2 — DETALHADA
        Estrutura:
        1. Resumo executivo
        2. Cenário macro e benchmarks
        3. Leitura da carteira e aderência ao perfil
        4. Recomendações por classe
        5. Riscos e próximos passos
        6. Aviso regulatório

        Adapte o tom ao perfil:
        - conservador: segurança, previsibilidade, liquidez
        - moderado: equilíbrio risco x retorno
        - arrojado: crescimento, volatilidade, diversificação

        CLIENTE
        - Nome: {client['nome']}
        - Idade: {client['idade']}
        - Profissão: {client['profissao']}
        - Perfil suitability: {client['perfil_suitability']}
        - Score suitability: {client['score_suitability']}
        - Objetivo: {client['objetivo_investimento']}
        - Horizonte: {client['horizonte_tempo']}
        - Tolerância a risco: {client['tolerancia_risco']}
        - Conhecimento em investimentos: {client['conhecimento_investimentos']}
        - Patrimônio total: R$ {client['patrimonio_total']}
        - Valor aplicado: R$ {client['valor_aplicado']}
        - Produtos ativos: {client['produtos_ativos']}
        - Rentabilidade 12m: {client['rentabilidade_12m']}%
        - Evento recente: {client['evento_ocorrido']} (confiança {client['score_confianca']})
        - Preferência de canal: {client['canal_preferencia']}

        MERCADO BASE
        - CDI 12m: {state['market_snapshot']['cdi_12m']}%
        - Ibovespa 12m: {state['market_snapshot']['ibovespa_12m']}%
        - IFIX 12m: {state['market_snapshot']['ifix_12m']}%
        - IMA-B 12m: {state['market_snapshot']['ima_b_12m']}%

        ALOCAÇÃO SUGERIDA
        {allocation_lines}

        {benchmark_block}

        CONHECIMENTO RECUPERADO VIA RAG
        {rag_context}

        Devolva exatamente no formato:
        ### RESUMO
        ...
        ### DETALHADO
        ...
        """
    ).strip()

    logger.debug("Prompt final montado com %s blocos RAG", len(rag_blocks))

    return {**state, "report_prompt": prompt}


def _fallback_report(state: dict) -> str:
    client = state["client"]
    allocations: str = ", ".join(
        [f"{item['classe']} ({item['peso']}%)" for item in state["recommended_allocation"]]
    )
    return dedent(
        f"""
        Resumo executivo
        {client['nome']} possui perfil {client['perfil_suitability'].lower()} e objetivo de {client['objetivo_investimento'].lower()}. O horizonte informado é {client['horizonte_tempo'].lower()}, com patrimônio total de R$ {client['patrimonio_total']} e valor aplicado de R$ {client['valor_aplicado']}.

        Leitura da carteira
        A carteira atual mostra exposição a {client['produtos_ativos']}. A recomendação deve observar o suitability, o evento recente de {client['evento_ocorrido']} e a tolerância a risco {client['tolerancia_risco'].lower()}.

        Recomendações
        Uma carteira de referência compatível com o perfil é: {allocations}. O racional é equilibrar adequação ao perfil, diversificação e coerência com o horizonte de investimento.

        Riscos e próximos passos
        Recomenda-se revisão periódica, confirmação do enquadramento e validação humana antes da formalização. Oscilações de mercado podem ocorrer e a estratégia deve ser recalibrada em caso de mudança de renda, liquidez ou objetivos.

        Aviso regulatório
        Este material é informativo, não representa promessa de rentabilidade futura e depende de validação final do Banco XYZ.
        """
    ).strip()

def _build_benchmark_block(state: dict) -> str:
    benchmarks = state.get("benchmarks", {}) or {}
    current_rates = benchmarks.get("current_rates", {}) or {}

    return dedent(
        f"""
        BENCHMARKS EXTERNOS
        - Selic atual: {current_rates.get('selic')}
        - CDI atual: {current_rates.get('cdi')}
        - IPCA atual: {current_rates.get('ipca')}
        - Histórico Ibovespa disponível: {"sim" if benchmarks.get("ibov_history") else "não"}
        """
    ).strip()

def _split_report_versions(full_report: str) -> dict[str, str]:
    if "### RESUMO" in full_report and "### DETALHADO" in full_report:
        try:
            _, rest = full_report.split("### RESUMO", 1)
            summary_part, detailed_part = rest.split("### DETALHADO", 1)
            return {
                "report_summary": summary_part.strip(),
                "report_detailed": detailed_part.strip(),
            }
        except ValueError:
            pass

    paragraphs = [p.strip() for p in full_report.split("\n\n") if p.strip()]
    summary = "\n\n".join(paragraphs[:3]) if paragraphs else full_report

    return {
        "report_summary": summary,
        "report_detailed": full_report,
    }


def _build_mock_portfolio_history(state: dict) -> list[dict]:
    profile = str(state["client"]["perfil_suitability"]).lower()
    if "conserv" in profile:
        growth = [100.0, 100.6, 101.2, 101.9, 102.5, 103.1, 103.8]
    elif "moder" in profile:
        growth = [100.0, 101.0, 100.8, 102.3, 103.4, 103.0, 104.2]
    else:
        growth = [100.0, 102.5, 99.8, 104.0, 101.2, 106.0, 108.5]

    labels = [
        "2025-10-01",
        "2025-11-01",
        "2025-12-01",
        "2026-01-01",
        "2026-02-01",
        "2026-03-01",
        "2026-04-01",
    ]

    return [{"date": d, "portfolio": v} for d, v in zip(labels, growth)]


def draft_report(state: dict) -> dict:
    report_text = generate_text(state["report_prompt"], _fallback_report(state))
    versions = _split_report_versions(report_text)

    profile = state["client"]["perfil_suitability"]
    portfolio_history = _build_mock_portfolio_history(state)
    benchmarks = build_portfolio_vs_benchmarks(
        profile=profile,
        portfolio_series=portfolio_history,
    )
    chart_recommendation = build_profile_chart_recommendation(profile)

    artifacts = state.get("artifacts", {}) or {}
    artifacts["benchmarks"] = benchmarks
    artifacts["chart_recommendation"] = chart_recommendation
    artifacts["recommended_allocation"] = state.get("recommended_allocation", [])

    audit = state.get("audit_log", []) + [
        {
            "step": "draft_report",
            "at": utc_now_iso(),
            "mode": "azure_or_fallback",
            "report_versions": ["summary", "detailed"],
        }
    ]

    return {
        **state,
        **versions,
        "report_text": report_text,
        "report_preview": versions["report_summary"],
        "artifacts": artifacts,
        "approval_status": "pending",
        "audit_log": audit,
    }

def process_report(state):
    return build_contact_messages(state)

def approval_gate(state: dict) -> dict:
    approved = state.get("approval_status") == "approved"
    audit = state.get("audit_log", []) + [
        {
            "step": "approval_gate",
            "at": utc_now_iso(),
            "approved": approved,
            "approver_name": state.get("approver_name", "Analista Humano"),
            "notes": state.get("approval_notes") or "Sem observações",
        }
    ]
    return {**state, "audit_log": audit}
