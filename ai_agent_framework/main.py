from langchain_core.messages import HumanMessage
from rich.console import Console
from rich.panel import Panel

from app.agent import build_agent

console = Console()

agent = build_agent()

console.print(Panel("AI Agent Framework iniciado 🚀"))

while True:

    user_input = console.input("\n[bold blue]User:[/bold blue] ")

    if user_input.lower() in ["exit", "quit"]:
        break

    response = agent.invoke(
        {"messages": [HumanMessage(content=user_input)]}
    )

    for message in response["messages"]:

        if message.type == "ai":
            console.print(
                Panel(message.content, title="AI", border_style="green")
            )