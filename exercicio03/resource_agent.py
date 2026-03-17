from exercicio03.base_agent import Agent


class ResourceAgent(Agent):
    def __init__(self, name, bus, llm=None):
        super().__init__(name, bus, llm)
        self.recursos = {
            "ambulancias": 5,
            "barcos": 3,
            "combustivel": 100
        }

    async def receive(self, event_type, data):
        if event_type == "RESGATE":
            decisao = await self.llm.decide(self.recursos)

            self.log(f"LLM decidiu uso: {decisao} 🧠")

            if self.recursos["combustivel"] > 10:
                self.recursos["combustivel"] -= 10
                await self.bus.publish("RECURSOS_OK", self.recursos)
            else:
                await self.bus.publish("FALHA", self.recursos)