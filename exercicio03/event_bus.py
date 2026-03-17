import asyncio
from collections import defaultdict

class EventBus:
    def __init__(self):
        self.subscribers = defaultdict(list)

    def subscribe(self, event_type, agent):
        self.subscribers[event_type].append(agent)

    async def publish(self, event_type, data):
        print(f"\n📡 EVENTO: {event_type} -> {data}")
        tasks = []
        for agent in self.subscribers[event_type]:
            tasks.append(asyncio.create_task(agent.receive(event_type, data)))
        await asyncio.gather(*tasks)