import asyncio

from backend.agents.research.hypothesis_generator import generate
from backend.agents.research.experiment_runner import run
from backend.agents.research.evaluator import evaluate
from backend.agents.research.evolution_engine import evolve


async def research_loop():
    while True:
        hypothesis = await generate()
        result = await run(hypothesis)
        score = await evaluate(result)
        await evolve(hypothesis, score)
        await asyncio.sleep(60)
