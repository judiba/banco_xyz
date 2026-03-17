# =========================
#  2(LANGGRAPH ASYNC STREAM)
# =========================

import asyncio
from typing import TypedDict
from langgraph.graph import StateGraph, END

# =========================
# STATE
# =========================
class FloodState(TypedDict):
    agua: int
    clima: str
    prioridade: str
    status_recursos: str


# =========================
# NODES (SEM PRINTS)
# =========================

async def sensor_node(state: FloodState):
    return {"agua": 80, "clima": "tempestade"}


async def traffic_node(state: FloodState):
    return {}


async def rescue_node(state: FloodState):
    return {"prioridade": "CRÍTICA"}


async def resource_node(state: FloodState):
    return {"status_recursos": "OK"}


async def coordinator_node(state: FloodState):
    return {}


# =========================
# BUILD GRAPH
# =========================

graph = StateGraph(FloodState)

graph.add_node("Sensor", sensor_node)
graph.add_node("Tráfego", traffic_node)
graph.add_node("Resgate", rescue_node)
graph.add_node("Recursos", resource_node)
graph.add_node("Coordenador", coordinator_node)

graph.set_entry_point("Sensor")

graph.add_edge("Sensor", "Tráfego")
graph.add_edge("Sensor", "Resgate")
graph.add_edge("Resgate", "Recursos")

def route_resources(state: FloodState):
    # garante que a condição seja avaliada no estado atual
    if state.get("status_recursos") == "OK":
        return "Coordenador"
    return "Resgate"

graph.add_conditional_edges("Recursos", route_resources)

graph.add_edge("Tráfego", "Coordenador")
graph.add_edge("Coordenador", END)

app = graph.compile()


# =========================
# ASCII FLOW (FIXO)
# =========================

def draw_ascii():
    print("\n📦 LANGGRAPH FLOW (ASCII ART):\n")

    diagram = r"""
                +-----------+
                | __start__ |
                +-----------+
                      |
                      |
                      v
                +-----------+
                |  Sensor   |
                +-----------+
                   /     \
                  /       \
                 v         v
        +-----------+   +-----------+
        |  Tráfego  |   |  Resgate  |
        +-----------+   +-----------+
                \         /
                 \       /
                  v     v
                +-----------+
                | Recursos  |
                +-----------+
                      |
                      v
                +--------------+
                | Coordenador  |
                +--------------+
                      |
                      v
                +-----------+
                |  __end__  |
                +-----------+
"""
    print(diagram)


# =========================
# ASYNC STREAM EXECUTION
# =========================
async def run_stream():
    async for event in app.astream({}):
        for step, value in event.items():
            print(f"➡️ {step}: {value}")


# =========================
# MAIN
# =========================
async def main():
    await run_stream()
    draw_ascii()


if __name__ == "__main__":
    asyncio.run(main())
