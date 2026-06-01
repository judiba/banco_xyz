from strands import Agent
from backend.app_config.bedrock import create_bedrock_model
from backend.prompts.fallback import FALLBACK_PROMPT_V1

_AGENT = None


def get_fallback_agent():
    global _AGENT

    if _AGENT is None:
        _AGENT = Agent(
            model=create_bedrock_model(),
            system_prompt=FALLBACK_PROMPT_V1,
            tools=[],
        )

    return _AGENT
