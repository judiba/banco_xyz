async def evaluate(result):
    quality = result.metrics.get("answer_score", 0)

    return quality
