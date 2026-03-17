from exercicio03.base_agent import Agent


class RescueAgent(Agent):
    async def receive(self, event_type, data):
        if event_type == "ALERTA_ENCHENTE":
            prioridade = await self.llm.decide(data)
            self.log(f"Prioridade definida: {prioridade} 🚑")

            await self.bus.publish("RESGATE", {
                "prioridade": prioridade
            })