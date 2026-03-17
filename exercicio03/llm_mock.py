import asyncio
import random

class MockLLM:
    async def decide(self, context):
        await asyncio.sleep(0.2)
        return random.choice([
            "ALTA",
            "MÉDIA",
            "CRÍTICA"
        ])