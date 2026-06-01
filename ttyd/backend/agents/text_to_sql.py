from strands import Agent
from backend.app_config.bedrock import create_bedrock_model
# from tools.rag_context import rag_context
# from tools.redshift_gateway import run_redshift_select


_TEXT_TO_SQL_AGENT = None


# def get_text_to_sql_agent():
# global _TEXT_TO_SQL_AGENT

# if _TEXT_TO_SQL_AGENT is None:
# _TEXT_TO_SQL_AGENT = Agent(
# model = create_bedrock_model(),
# tools=[
# rag_context,
# run_redshift_select,
# ],
# )

# return _TEXT_TO_SQL_AGENT


def get_text_to_sql_agent():
    global _TEXT_TO_SQL_AGENT

    if _TEXT_TO_SQL_AGENT is None:
        _TEXT_TO_SQL_AGENT = Agent(model=create_bedrock_model(), tools=[])

    return _TEXT_TO_SQL_AGENT
