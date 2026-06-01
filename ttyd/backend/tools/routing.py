from typing import Any
import re
from strands import tool


from application.rag_service import get_rag_agent
from backend.agents.text_to_sql import get_text_to_sql_agent
from backend.agents.fallback import get_fallback_agent
from backend.agents.table_selector_agent import get_table_selector_agent
from backend.agents.column_selector_agent import get_column_selector_agent

from backend.prompts.text_to_sql import build_text_to_sql_prompt
from tools.schema_tool import selecionar_tabela_yaml
from backend.infrastructure.rds.redshift_adapter import run_redshift_select


@tool
def call_rag(question: str) -> str:
    print("entrou na tool: call_rag")
    agent = get_rag_agent()
    response = agent(question)
    return extract_text(response)


def extract_text(response: Any) -> str:
    if hasattr(response, "message"):
        msg = response.message
    else:
        msg = response

    if isinstance(msg, dict):
        for block in msg.get("content", []):
            if isinstance(block, dict) and "text" in block:
                return str(block["text"]).strip()

    if isinstance(msg, str):
        return msg.strip()

    return str(msg).strip()


def sanitize_sql(sql: str) -> str:
    if not sql:
        return ""

    match = re.search(r"```(?:sql|text)?\s*(.*?)\s*```", sql, re.DOTALL | re.IGNORECASE)
    if match:
        sql = match.group(1)

    sql = sql.replace("```", "")
    sql = re.sub(r"^\s*sql\s*$", "", sql, flags=re.IGNORECASE | re.MULTILINE)
    sql = re.sub(r"--.*", "", sql)
    sql = re.sub(r";+\s*$", "", sql)

    return sql.strip()


def selecionar_tabela(question: str) -> str | None:
    agent = get_table_selector_agent()
    res = agent(question)
    tabela_texto = extract_text(res)

    if not tabela_texto:
        return None

    tabela_texto = tabela_texto.replace("TABELA:", "").strip()
    tabela_texto = tabela_texto.split("\n")[0].strip()

    return tabela_texto or None


def selecionar_colunas(pergunta: str, tabela: str, schema: str) -> list[str] | None:
    agent = get_column_selector_agent()

    prompt = f"""
Pergunta do usuário:
{pergunta}

Tabela: {tabela}

Schema disponível:
{schema}

Retorne apenas os nomes das colunas necessários,
separados por vírgula.
Sem explicação.
Sem texto adicional.
"""

    res = agent(prompt)
    resposta = extract_text(res)

    if not resposta:
        return None

    resposta = resposta.replace("COLUNAS:", "").strip()
    resposta = resposta.replace("\n", ",")

    colunas = [c.strip() for c in resposta.split(",") if c.strip()]
    return colunas if colunas else None


def filtrar_schema(schema: str, colunas_escolhidas: list[str]) -> str:
    linhas = schema.split("\n")
    resultado: list[str] = []

    for linha in linhas:
        for col in colunas_escolhidas:
            if re.search(rf"\b{re.escape(col)}\b", linha):
                resultado.append(linha.strip())

    return "\n".join(sorted(set(resultado)))


def gerar_sql(pergunta: str, tabela: str, schema_filtrado: str) -> str:
    agent = get_text_to_sql_agent()
    tabela_completa = f"star_schema_espinha.agg_tables.{tabela}"

    prompt = build_text_to_sql_prompt(
        pergunta=pergunta,
        tabela_completa=tabela_completa,
        schema_filtrado=schema_filtrado,
    )

    res = agent(prompt)
    return extract_text(res)


@tool
def call_text_to_sql(question: str) -> str:
    print("entrou na tool: call_text_to_sql")

    if not question or not isinstance(question, str):
        return "Pergunta inválida."

    question = question.strip()

    tabela = selecionar_tabela(question)
    if not tabela:
        return "Não foi possível determinar a tabela adequada."

    schema_completo = selecionar_tabela_yaml(tabela)
    if not schema_completo:
        return "Não foi possível carregar o schema da tabela."

    colunas = selecionar_colunas(question, tabela, schema_completo)
    if not colunas:
        return "Não foi possível determinar as colunas necessárias."

    schema_filtrado = filtrar_schema(schema_completo, colunas)
    if not schema_filtrado:
        return "Nenhuma coluna válida encontrada no schema."

    sql_query_raw = gerar_sql(question, tabela, schema_filtrado)

    try:
        sql_query = sanitize_sql(sql_query_raw)
    except Exception as e:
        return str(e)

    if not re.match(r"^select\b", sql_query, re.IGNORECASE):
        print("SQL inválida após sanitize:", repr(sql_query))
        return "Falha ao gerar SQL válida."

    try:
        resultado = run_redshift_select(sql=sql_query)
    except Exception as e:
        resultado = str(e)

    if isinstance(resultado, str) and "error" in resultado.lower():
        tabela_completa = f"star_schema_espinha.agg_tables.{tabela}"

        retry_prompt = f"""
A SQL abaixo gerou erro:

{sql_query}

Erro:
{resultado}

Corrija respeitando:
- Apenas SELECT
- Apenas tabela {tabela_completa}
- Apenas colunas permitidas
- Use GROUP BY 1
- Use ORDER BY 1
- Não usar SELECT *
- Nunca use alias no ORDER BY

Retorne apenas a SQL corrigida.
"""

        agent = get_text_to_sql_agent()
        res_retry = agent(retry_prompt)
        sql_corrigida = extract_text(res_retry)

        try:
            sql_corrigida = sanitize_sql(sql_corrigida)
            if not re.match(r"^(select|with)\b", sql_corrigida, re.IGNORECASE):
                return "Falha ao corrigir SQL."

            resultado = run_redshift_select(sql=sql_corrigida)

        except Exception as e:
            return str(e)

    if not resultado:
        return "0 linhas retornadas"

    return str(resultado)


@tool
def call_fallback(question: str) -> str:
    print("entrou na tool: call_fallback")
    agent = get_fallback_agent()
    response = agent(question)
    return extract_text(response)
