import os
import logging

from dotenv import load_dotenv
from langchain_classic.agents import AgentExecutor, create_tool_calling_agent
from langchain_classic.memory import ConversationBufferMemory
from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder 
from langchain_core.tools import tool

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

llm = AzureChatOpenAI(
    azure_deployment=os.getenv("OPENAI_MODEL"),
    api_version=os.getenv("AZURE_OPENAI_VERSION"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_KEY"),

    
)

@tool
def buscar_documentacao(query: str) -> str:
    """Busca na documentação técnica do produto."""
    docs = {
        "instalação": "Para instalar, execute: pip install ...",
        "configuração": "Configure o arquivo .env com...",
        "erro 500": "Erro 500 geralmente indica..."
    }
    for chave, valor in docs.items():
        if chave in query.lower():
            return valor
    return "Documentação não encontrada para esta query."

@tool
def calcular_custo_tokens(num_tokens: int, modelo: str) -> str:
    """Calcula o custo estimado de uso baseado em tokens."""
    precos = {"gpt-4o": 0.005, "gpt-4o-mini": 0.0002}
    preco = precos.get(modelo, 0.005)
    custo = (num_tokens / 1000) * preco
    return f"Custo estimado: ${custo:.4f} para {num_tokens} tokens"

@tool  
def gerar_email(assunto: str, pontos: str) -> str:
    """Gera rascunho de e-mail de suporte."""
    
    logger.info(f"Tool gerar_email chamada: {assunto}")

    return (f"Assunto: {assunto}\n\n"
            f"Prezado(a),\n\n{pontos}\n\nAtenciosamente.")

tools = [buscar_documentacao, calcular_custo_tokens, gerar_email]

memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True
)

prompt = ChatPromptTemplate.from_messages([
    ("system", 
     "Você é um assistente de suporte técnico. "
     "Use as ferramentas disponíveis para ajudar o usuário. "
     "Sempre que resolver um problema, ofereça enviar "
     "um resumo por e-mail."),    
    ("human", "{input}"),
    MessagesPlaceholder("agent_scratchpad"),
])

agent = create_tool_calling_agent(llm, tools, prompt)

executor = AgentExecutor(agent=agent, tools=tools, memory=memory, verbose=True)

print("\nAgente iniciado. Digite 'sair' para encerrar.\n")

while True:

    pergunta = input("Sua Pergunta: ")

    if pergunta.lower() in ["sair", "exit", "quit"]:
        break

    resposta = executor.invoke({
        "input": pergunta
    })

    print("\nAgente:", resposta["output"], "\n")
    
# Teste 1: Pergunta simples (1 tool)

#  Como faço a instalação?

# Teste 2: Pergunta que exige 2 tools

# Estou com erro 500 e quero saber quanto custaria processar 50 mil tokens no gpt-4o

# Teste 3: Cenário completo (3 tools)

#Busque como resolver o erro 500, calcule o custo de 100K tokens no gpt-4o-mini e gere um e-mail para o cliente com o diagnóstico