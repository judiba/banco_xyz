from strands import Agent
from backend.app_config.bedrock import create_bedrock_model
from backend.app_config.descricao import yaml_to_prompt_string
from backend.prompts.table_selector import TABLE_SELECTOR_PROMPT
from backend.app_config.settings import settings

_TABLE_SELECTOR_AGENT = None


def get_table_selector_agent():
    global _TABLE_SELECTOR_AGENT

    if _TABLE_SELECTOR_AGENT is None:
        model = create_bedrock_model()

        desc_tables_string = yaml_to_prompt_string(
            settings.YAML_PATH_TABLES  # ← desc_tables.yaml
        )

        system_prompt = f"""
           {TABLE_SELECTOR_PROMPT}

            Tabelas disponíveis:
               {desc_tables_string}
          """

        _TABLE_SELECTOR_AGENT = Agent(
            model=model,
            system_prompt=system_prompt,
            tools=[],  # ✅ nunca usar tools aqui
        )

    return _TABLE_SELECTOR_AGENT
