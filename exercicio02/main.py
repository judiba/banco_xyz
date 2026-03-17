def main():
    print("Hello from exercicio02!")


if __name__ == "__main__":
    main()

import random
import time
from collections import defaultdict
from dataclasses import dataclass, field

# =========================
# EVENT BUS (mensageria)
# =========================

class EventBus:
    def __init__(self):
        self.subscribers = defaultdict(list)

    def subscribe(self, event_type, agent):
        self.subscribers[event_type].append(agent)

    def publish(self, event_type, data):
        print(f"\n📡 EVENTO: {event_type} -> {data}")
        for agent in self.subscribers[event_type]:
            agent.receive(event_type, data)


# =========================
# BASE AGENTE
# =========================

class Agent:
    def __init__(self, name, bus):
        self.name = name
        self.bus = bus

    def receive(self, event_type, data):
        pass

    def log(self, msg):
        print(f"[{self.name}] {msg}")


# =========================
# AGENTES SENSORES
# =========================

class SensorAgent(Agent):
    def monitor(self):
        nivel_agua = random.randint(0, 100)
        clima = random.choice(["chuva", "normal", "tempestade"])
        trafego = random.randint(0, 100)

        self.log(f"Monitorando... Água={nivel_agua}, Clima={clima}, Tráfego={trafego}")

        if nivel_agua > 70 or clima == "tempestade":
            self.bus.publish("ALERTA_ENCHENTE", {
                "agua": nivel_agua,
                "clima": clima,
                "trafego": trafego
            })


# =========================
# AGENTES DE TRÁFEGO
# =========================

class TrafficAgent(Agent):
    def receive(self, event_type, data):
        if event_type == "ALERTA_ENCHENTE":
            self.log("Recalculando rotas e liberando semáforos 🚦")
            self.bus.publish("ROTAS_ATUALIZADAS", {"status": "ok"})


# =========================
# AGENTES DE RESGATE
# =========================

class RescueAgent(Agent):
    def receive(self, event_type, data):
        if event_type == "ALERTA_ENCHENTE":
            prioridade = "ALTA" if data["agua"] > 80 else "MÉDIA"
            self.log(f"Definindo prioridade: {prioridade} 🚑")
            self.bus.publish("RESGATE_INICIADO", {
                "prioridade": prioridade
            })


# =========================
# AGENTES DE RECURSOS
# =========================

class ResourceAgent(Agent):
    def __init__(self, name, bus):
        super().__init__(name, bus)
        self.recursos = {
            "ambulancias": 5,
            "barcos": 3,
            "combustivel": 100
        }

    def receive(self, event_type, data):
        if event_type == "RESGATE_INICIADO":
            self.log("Redistribuindo recursos 🧰")

            if self.recursos["combustivel"] > 20:
                self.recursos["combustivel"] -= 20
                self.bus.publish("RECURSOS_ALOCADOS", self.recursos)
            else:
                self.bus.publish("FALTA_RECURSOS", self.recursos)


# =========================
# COORDENADOR GLOBAL
# =========================

class CoordinatorAgent(Agent):
    def __init__(self, name, bus):
        super().__init__(name, bus)
        self.estado_global = {}

    def receive(self, event_type, data):
        self.log(f"Atualizando estado global com {event_type}")

        self.estado_global[event_type] = data

        if event_type == "FALTA_RECURSOS":
            self.log("⚠️ Conflito detectado! Priorizando áreas críticas")

        if event_type == "RECURSOS_ALOCADOS":
            self.log("✅ Operação fluindo")


# =========================
# GRAFO (visual ASCII)
# =========================

class AgentGraph:
    def __init__(self):
        self.edges = []

    def add_edge(self, a, b):
        self.edges.append((a, b))

    def draw_ascii(self):
        print("\n🔗 GRAFO DE INTERAÇÃO:")
        for a, b in self.edges:
            print(f"{a} ---> {b}")

    def get_graph(self):
        return self


# =========================
# SETUP DO SISTEMA
# =========================

def build_system():
    bus = EventBus()

    sensor = SensorAgent("Sensor", bus)
    traffic = TrafficAgent("Tráfego", bus)
    rescue = RescueAgent("Resgate", bus)
    resource = ResourceAgent("Recursos", bus)
    coordinator = CoordinatorAgent("Coordenador", bus)

    # Inscrições
    bus.subscribe("ALERTA_ENCHENTE", traffic)
    bus.subscribe("ALERTA_ENCHENTE", rescue)
    bus.subscribe("RESGATE_INICIADO", resource)
    bus.subscribe("RECURSOS_ALOCADOS", coordinator)
    bus.subscribe("FALTA_RECURSOS", coordinator)

    # Grafo
    graph = AgentGraph()
    graph.add_edge("Sensor", "Tráfego")
    graph.add_edge("Sensor", "Resgate")
    graph.add_edge("Resgate", "Recursos")
    graph.add_edge("Recursos", "Coordenador")

    return sensor, graph


# =========================
# EXECUÇÃO
# =========================

if __name__ == "__main__":
    sensor, graph = build_system()

    # Simulação contínua
    for _ in range(5):
        sensor.monitor()
        time.sleep(1)

    # Visualizar grafo
    graph.get_graph().draw_ascii()