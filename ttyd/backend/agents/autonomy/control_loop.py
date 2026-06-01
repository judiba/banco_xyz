import asyncio
from backend.agents.autonomy.planner import plan
from backend.agents.autonomy.evaluator import evaluate
from backend.agents.autonomy.self_heal import heal


async def autonomous_loop():
    while True:
        decision = await plan()

        result = await decision.execute()

        score = await evaluate(result)

        if score < 0.7:
            await heal(result)

        await asyncio.sleep(5)
