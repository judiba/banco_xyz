from strands import Agent
from backend.app_config.bedrock import create_bedrock_model
from backend.prompts.fallback import FALLBACK_PROMPT_V1

_AGENT = None


def get_fallback_agent():
    """
    Returns the fallback agent.

    The fallback agent is used when the main agent cannot answer the question.

    Returns:
        Agent: The fallback agent
    """
    global _AGENT

    if _AGENT is None:
        _AGENT = Agent(
            model=create_bedrock_model(),
            system_prompt=FALLBACK_PROMPT_V1,
            tools=[],
        )

    return _AGENT


__all__ = ["get_fallback_agent"]


def get_fallback_agent(question: str):
    """
    Returns the fallback agent for a given question.

    The fallback agent is used when the main agent cannot answer the question.

    Args:
        question: The question to answer

    Returns:
        Agent: The fallback agent
    """
    if _AGENT is None:
        _AGENT = Agent(
            model=create_bedrock_model(),
            system_prompt=FALLBACK_PROMPT_V1,
            tools=[],
        )

    return _AGENT
