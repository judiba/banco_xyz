from langgraph.checkpoint.memory import MemorySaver


def get_memory():
    """
    Creates an in-memory checkpoint system for the agent.
    This stores conversation state between turns.
    """

    memory = MemorySaver()

    return memory