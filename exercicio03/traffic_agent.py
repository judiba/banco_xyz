from exercicio03.base_agent import Agent


class TrafficAgent(Agent):
    async def receive(self, event_type, data):
        if event_type == "ALERTA_ENCHENTE":
            self.log("Otimizando rotas 🚦")
            await self.bus.publish("ROTAS_OK", {"status": "ok"})
