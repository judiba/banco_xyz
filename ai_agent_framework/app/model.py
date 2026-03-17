import os
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI

load_dotenv()

def get_model():

    return AzureChatOpenAI(
        azure_endpoint=os.getenv("AZURE_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version="2025-01-01-preview",
        model=os.getenv("MODEL_NAME", "gpt-5-nano"),
        temperature=0.2,
        streaming=True
    )