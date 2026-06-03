from strands import Agent
from backend.app_config.bedrock import create_bedrock_model
from backend.prompts.column_selector import COLUMN_SELECTOR_PROMPT

_COLUMN_SELECTOR_AGENT = None


def get_column_selector_agent():
    """
    Returns the column selector agent.

    The column selector agent is used to select the columns to be used in the query.

    Returns:
        Agent: The column selector agent
    """
    global _COLUMN_SELECTOR_AGENT

    if _COLUMN_SELECTOR_AGENT is None:
        model = create_bedrock_model()

        _COLUMN_SELECTOR_AGENT = Agent(
            model=model,
            system_prompt=COLUMN_SELECTOR_PROMPT,
            tools=[],
        )

    return _COLUMN_SELECTOR_AGENT       

__all__ = ["get_column_selector_agent"]
