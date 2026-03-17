import asyncio
import random

from exercicio03.base_agent import Agent

class SensorAgent(Agent):
    async def run(self):
        while True:
            nivel_agua = random.randint(0, 100)
            clima = random.choice(["chuva", "normal", "tempestade"])

            self.log(f"Água={nivel_agua}, Clima={clima}")

            if nivel_agua > 70 or clima == "tempestade":
                await self.bus.publish("ALERTA_ENCHENTE", {
                    "agua": nivel_agua,
                    "clima": clima
                })

            await asyncio.sleep(1)