import os
from typing import Annotated
import requests

from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from langchain_core.messages import HumanMessage
from langchain.agents import create_agent

# --------------------------------------------------
# Load environment variables
# --------------------------------------------------

load_dotenv()

#AZURE_ENDPOINT = os.getenv("AZURE_ENDPOINT")
#AZURE_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")

#if not AZURE_ENDPOINT or not AZURE_API_KEY:
#    raise ValueError("Missing AZURE_ENDPOINT or AZURE_OPENAI_API_KEY in .env file")

# --------------------------------------------------
# Model configuration
# --------------------------------------------------

model = AzureChatOpenAI(
    azure_endpoint=os.getenv("AZURE_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),  
    api_version="2025-01-01-preview",
    model="gpt-5-nano",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)

# --------------------------------------------------
# Tools
# --------------------------------------------------

def get_webpage() -> str:
    """
    Gets the HTML webpage for the bible API
    """
    return requests.get("https://bible-api.com/").text


def make_request(
    route: Annotated[str, "The specific desired route (for example, /john+3:16)"]
) -> str:
    """
    Makes a request to the bible API with the given route
    """
    url = f"https://bible-api.com{route}"
    return requests.get(url).text


# --------------------------------------------------
# Agent
# --------------------------------------------------

agent = create_agent(
    system_prompt="""
Você é um assistente que pode fazer requisições para a API da bíblia.

Você possui duas ferramentas:

1. get_webpage
   Retorna o HTML da página principal da API da bíblia.

2. make_request
   Recebe uma rota da API e retorna os dados.

Use get_webpage primeiro caso precise entender como a API funciona.
Use make_request quando precisar buscar versículos ou capítulos.

Se algo solicitado não existir na API, explique ao usuário e ofereça
alternativas disponíveis.
""",
    tools=[get_webpage, make_request],
    model=model,
)

# --------------------------------------------------
# Terminal colors
# --------------------------------------------------

BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"

CYAN = "\033[36m"
YELLOW = "\033[33m"
GREEN = "\033[32m"
MAGENTA = "\033[35m"
BLUE = "\033[34m"

# --------------------------------------------------
# Chat loop
# --------------------------------------------------

print(f"{BOLD}Bible API Agent started. Type 'exit' to quit.{RESET}")

while True:
    user_input = input(f"\n{BOLD}{BLUE}User:{RESET} ")

    if user_input.lower() in ["exit", "quit"]:
        print("Exiting the agent.")
        break

    response = agent.invoke(
        {
            "messages": [
                HumanMessage(content=user_input)
            ]
        }
    )

    print()

    for message in response["messages"]:
        mtype = type(message).__name__

        if mtype == "SystemMessage":
            print(f"{BOLD}{MAGENTA}[SYSTEM]{RESET}")
            print(f"{DIM}{message.content}{RESET}")

        elif mtype == "HumanMessage":
            print(f"{BOLD}{BLUE}[USER]{RESET}")
            print(message.content)

        elif mtype == "AIMessage":
            tool_calls = getattr(message, "tool_calls", [])

            if tool_calls:
                for tc in tool_calls:
                    print(f"{BOLD}{YELLOW}[TOOL CALL]{RESET} {tc['name']}")
                    print(f"  args: {tc['args']}")

            if message.content:
                print(f"{BOLD}{GREEN}[AI]{RESET}")
                print(message.content)

        elif mtype == "ToolMessage":
            print(f"{BOLD}{CYAN}[TOOL RESPONSE]{RESET} (name={message.name})")

            truncated = str(message.content)[:300]

            if len(str(message.content)) > 300:
                truncated += f"{DIM} ... ({len(str(message.content))} chars total){RESET}"

            print(truncated)

        print()