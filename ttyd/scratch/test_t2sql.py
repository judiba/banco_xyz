"""
Teste de integração do Agente T2SQL (DEV_OFFLINE).
Execute com: DEV_OFFLINE=true python scratch/test_t2sql.py
"""

import os

os.environ.setdefault("APP_ENV", "dev")
os.environ.setdefault("DEV_OFFLINE", "true")

from backend.agents.text_to_sql.agent import run_t2sql_pipeline
from backend.agents.text_to_sql.schema_catalog import get_schema_catalog
from backend.agents.text_to_sql.executor import execute_sql


def test_schema_catalog():
    catalog = get_schema_catalog()
    assert isinstance(catalog, list), "Catálogo deve ser uma lista"
    print(f"✅ Schema catalog: {len(catalog)} tabela(s) carregada(s)")
    for t in catalog:
        print(f"   - {t['tabela']}: {len(t.get('colunas', []))} coluna(s)")


def test_executor_mock():
    result = execute_sql("SELECT canal, SUM(receita) FROM fato_vendas GROUP BY 1", lake="big_data")
    assert isinstance(result, list), "Resultado deve ser lista"
    assert len(result) > 0, "Resultado não pode ser vazio"
    print(f"✅ Executor mock: {len(result)} linha(s) retornada(s)")


def test_sql_safety():
    result = execute_sql("DROP TABLE fato_vendas", lake="big_data")
    assert "error" in result[0], "DDL deve ser rejeitado"
    print("✅ Segurança SQL: DROP TABLE corretamente rejeitado")


def test_pipeline():
    result = run_t2sql_pipeline(
        question="Qual o total de receita por canal nos últimos 3 meses?",
        lake="big_data",
    )
    assert "sql_gerada" in result, "Pipeline deve retornar SQL gerada"
    assert "resultados" in result, "Pipeline deve retornar resultados"
    assert result["modo"] == "dev_offline", "Modo deve ser dev_offline"
    print("✅ Pipeline T2SQL:")
    print(f"   Tabela: {result['tabela']}")
    print(f"   SQL: {result['sql_gerada'][:80]}...")
    print(f"   Resultados: {len(result['resultados'])} linha(s)")


if __name__ == "__main__":
    print("\n🔬 Testando Agente T2SQL (modo DEV_OFFLINE)\n")
    test_schema_catalog()
    test_executor_mock()
    test_sql_safety()
    test_pipeline()
    print("\n✅ Todos os testes do T2SQL passaram!\n")
