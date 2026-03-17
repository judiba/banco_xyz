def main():
    print("Hello from exercicio03!")


if __name__ == "__main__":
    asyncio.run(main())

import asyncio

from event_bus import EventBus
from sensor_agent import SensorAgent
from traffic_agent import TrafficAgent
from rescue_agent import RescueAgent
from resource_agent import ResourceAgent
from coordinator_agent import CoordinatorAgent
from llm_mock import MockLLM

async def main():
    bus = EventBus()
    llm = MockLLM()

    sensor = SensorAgent("Sensor", bus)
    traffic = TrafficAgent("Tráfego", bus)
    rescue = RescueAgent("Resgate", bus, llm)
    resource = ResourceAgent("Recursos", bus, llm)
    coordinator = CoordinatorAgent("Coordenador", bus)

    bus.subscribe("ALERTA_ENCHENTE", traffic)
    bus.subscribe("ALERTA_ENCHENTE", rescue)
    bus.subscribe("RESGATE", resource)
    bus.subscribe("RECURSOS_OK", coordinator)
    bus.subscribe("FALHA", coordinator)

    await asyncio.gather(
        sensor.run(),
    )
