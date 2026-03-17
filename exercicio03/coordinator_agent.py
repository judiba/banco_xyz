from exercicio03.base_agent import Agent


class CoordinatorAgent(Agent):
    async def receive(self, event_type, data):
        self.log(f"Recebido: {event_type}")

        if event_type == "FALHA":
            self.log("⚠️ Escassez detectada!")

        if event_type == "RECURSOS_OK":
            self.log("✅ Sistema operando")
