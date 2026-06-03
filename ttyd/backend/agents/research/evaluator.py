# backend/agents/research/evaluator.py
# This module contains the evaluator for the research loop.


async def evaluate(result):
    """
    Evaluates the given result.

    Args:
        result: The result of the experiment

    Returns:
        float: The score of the experiment
    """
    return result.get("quality", 0)


__all__ = ["evaluate"]
