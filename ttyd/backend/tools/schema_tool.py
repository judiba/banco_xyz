import yaml
from backend.app_config.settings import settings


def selecionar_tabela_yaml(nome_tabela: str) -> str:
    """
    Retorna as colunas e descrições de uma tabela específica do schema.
    """

    with open(settings.YAML_PATH_COL, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if not data:
        return "YAML vazio ou inválido."

    tabelas = data.get("tabelas")

    if not tabelas:
        return "Chave 'tabelas' não encontrada no YAML."

    if nome_tabela not in tabelas:
        return f"Tabela '{nome_tabela}' não encontrada no YAML."

    detalhes = tabelas[nome_tabela]

    if not isinstance(detalhes, dict):
        return f"Estrutura inválida para a tabela '{nome_tabela}'."

    colunas = detalhes.get("colunas")

    if not colunas:
        return f"Tabela '{nome_tabela}' encontrada, mas não possui colunas definidas."

    linhas = [f"Tabela: {nome_tabela}", "Colunas:"]

    for coluna in colunas:
        nome = coluna.get("nome", "sem_nome")
        descricao = coluna.get("descricao", "Sem descrição")
        linhas.append(f"  - {nome}: {descricao}")

    return "\n".join(linhas)
