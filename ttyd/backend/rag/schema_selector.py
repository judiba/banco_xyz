from backend.app_config.descricao import yaml_to_prompt_string
from backend.app_config.settings import settings

desc_tables_string = yaml_to_prompt_string(settings.YAML_PATH_TABLES)

SCHEMA_SELECTOR_PROMPT = """
Você é um especialista em modelagem de dados no Amazon Redshift.

Tabelas disponíveis:
{desc_tables_string}

Sua tarefa:

1) Escolher APENAS UMA tabela adequada.
2) Selecionar apenas as colunas necessárias.

Retorne exclusivamente JSON válido no formato:

{{
  "tabela": "<nome_exato>",
  "colunas": ["coluna1", "coluna2"]
}}

Não explique.
Não escreva texto adicional.
"""


def get_schema_selector_prompt() -> str:
    """Retorna o prompt formatado com as tabelas disponíveis."""
    return SCHEMA_SELECTOR_PROMPT.format(desc_tables_string=desc_tables_string)
