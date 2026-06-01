"""
Testes de qualidade dos metadados YAML - LEVEL 19.

Objetivo:
- Validar sintaxe e estrutura dos arquivos YAML usados pela LLM.
- Manter o teste local/offline, sem dependência obrigatória de AWS/Glue.
- Separar validações corporativas reais para testes marcados como aws_real.
"""

from pathlib import Path
from typing import Any

import pytest
import yaml

from backend.app_config.settings import settings


def _load_yaml(path_value: str | Path) -> dict[str, Any]:
    """
    Carrega um YAML e garante que o conteúdo raiz seja um dicionário.
    """
    yaml_path = Path(path_value)

    assert yaml_path.exists(), f"Arquivo YAML não encontrado: {yaml_path}"
    assert yaml_path.is_file(), f"Caminho YAML não é um arquivo: {yaml_path}"

    with yaml_path.open("r", encoding="utf-8") as file:
        data = yaml.safe_load(file)

    assert data is not None, (
        f"O arquivo {yaml_path} está vazio ou contém YAML inválido."
    )

    assert isinstance(data, dict), (
        f"O conteúdo raiz de {yaml_path} deve ser um objeto YAML."
    )

    return data

def _iter_tabelas(data: dict[str, Any]) -> list[tuple[str, dict[str, Any]]]:
    """
    Normaliza o nó 'tabelas' aceitando os dois formatos encontrados no projeto:
    - LEVEL 18: tabelas como dict {nome_tabela: {...}}
    - LEVEL 19: tabelas como list [{nome: ..., ...}]
    """
    assert "tabelas" in data, "O YAML deve conter o nó raiz 'tabelas'."

    tabelas = data["tabelas"]

    if isinstance(tabelas, dict):
        normalized = []
        for nome, conteudo in tabelas.items():
            assert isinstance(conteudo, dict), f"A tabela '{nome}' deve ser um objeto."
            normalized.append((str(nome), conteudo))
        return normalized

    if isinstance(tabelas, list):
        normalized = []
        for index, conteudo in enumerate(tabelas):
            assert isinstance(conteudo, dict), f"A tabela na posição {index} deve ser um objeto."
            nome = conteudo.get("nome") or conteudo.get("name") or conteudo.get("tabela")
            assert nome, f"A tabela na posição {index} deve possuir 'nome', 'name' ou 'tabela'."
            normalized.append((str(nome), conteudo))
        return normalized

    pytest.fail("O nó 'tabelas' deve ser uma lista ou um mapeamento.")


def _validate_table_metadata(tabela_nome: str, tabela_conteudo: dict[str, Any]) -> None:
    """Valida metadados mínimos necessários para bom contexto da LLM."""
    descricao = tabela_conteudo.get("descricao") or tabela_conteudo.get("description")
    assert descricao, f"A tabela '{tabela_nome}' está sem descrição."

    colunas = tabela_conteudo.get("colunas") or tabela_conteudo.get("columns") or []
    assert isinstance(colunas, list), f"As colunas da tabela '{tabela_nome}' devem ser uma lista."

    for index, coluna in enumerate(colunas):
        assert isinstance(coluna, dict), (
            f"A coluna {index} da tabela '{tabela_nome}' deve ser um objeto."
        )

        coluna_nome = coluna.get("nome") or coluna.get("name")
        assert coluna_nome, (
            f"A coluna {index} da tabela '{tabela_nome}' deve possuir 'nome' ou 'name'."
        )

        coluna_descricao = coluna.get("descricao") or coluna.get("description")
        assert coluna_descricao, (
            f"A coluna '{coluna_nome}' da tabela '{tabela_nome}' está sem descrição."
        )


def test_validar_yaml_colunas_local_level19():
    """
    LEVEL 19: valida o YAML de colunas em modo local/offline.
    Não acessa AWS/Glue; apenas garante riqueza mínima de contexto para a LLM.
    """
    data = _load_yaml(settings.YAML_PATH_COL)
    tabelas = _iter_tabelas(data)

    assert tabelas, "O YAML de colunas deve mapear pelo menos uma tabela."

    for tabela_nome, tabela_conteudo in tabelas:
        _validate_table_metadata(tabela_nome, tabela_conteudo)


def test_validar_yaml_tabelas_local_level19():
    """
    LEVEL 19: valida o YAML de tabelas em modo local/offline.
    Aceita a estrutura legada dict e a estrutura nova em lista.
    """
    data = _load_yaml(settings.YAML_PATH_TABLES)
    tabelas = _iter_tabelas(data)

    assert tabelas, "O YAML de tabelas deve mapear pelo menos uma tabela."

    for tabela_nome, tabela_conteudo in tabelas:
        descricao = tabela_conteudo.get("descricao") or tabela_conteudo.get("description")
        assert descricao, f"A tabela '{tabela_nome}' está sem descrição."


@pytest.mark.aws_real
def test_validar_yaml_tabelas_aws_level19():
    """
    LEVEL 19: valida o YAML de tabelas em modo online/online.
    """
    data = _load_yaml(settings.YAML_PATH_TABLES)
    tabelas = _iter_tabelas(data)

    assert tabelas, "O YAML de tabelas deve mapear pelo menos uma tabela."

    for tabela_nome, tabela_conteudo in tabelas:
        _validate_table_metadata(tabela_nome, tabela_conteudo)

    print(
        "🚀 SUCESSO: O arquivo desc_tables.yaml possui sintaxe correta e mapeia devidamente os schemas exigidos pela LLM."
    )