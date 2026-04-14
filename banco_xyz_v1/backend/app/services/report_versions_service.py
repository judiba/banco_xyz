from __future__ import annotations

from textwrap import dedent


def split_report_versions(full_report: str) -> dict[str, str]:
    """
    Fallback simples:
    - summary: primeiros blocos
    - detailed: texto completo
    """
    paragraphs = [p.strip() for p in full_report.split("\n\n") if p.strip()]
    summary = "\n\n".join(paragraphs[:3]) if paragraphs else full_report

    return {
        "report_summary": summary,
        "report_detailed": full_report,
    }


def build_prompt_with_versions(
    client_block: str,
    market_block: str,
    benchmark_block: str,
    rag_block: str,
) -> str:
    return dedent(
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
        {client_block}

        MERCADO
        {market_block}

        BENCHMARKS
        {benchmark_block}

        RAG
        {rag_block}

        Devolva no formato:
        ### RESUMO
        ...
        ### DETALHADO
        ...
        """
    ).strip()