from dataclasses import dataclass
from typing import Any


@dataclass
class AutonomyResult:
    conversation_id: str
    status: str
    metrics: dict[str, Any]


async def evaluate(result: AutonomyResult) -> float:
    """
    Evaluates the result of an autonomous agent.

    Args:
        result: The result of the autonomous agent

    Returns:
        float: The quality of the result
    """
    return result.metrics.get("answer_score", 0)


__all__ = ["evaluate", "AutonomyResult"]
