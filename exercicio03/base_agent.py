class Agent:
    def __init__(self, name, bus, llm=None):
        self.name = name
        self.bus = bus
        self.llm = llm

    async def receive(self, event_type, data):
        pass

    def log(self, msg):
        print(f"[{self.name}] {msg}")