from dotenv import load_dotenv
from backend.app_config.settings import settings


def load_env():
    """
    Carrega variáveis de ambiente (.env para local,
    IAM Role no AgentCore).
    """
    load_dotenv()


def aws_region() -> str:
    return settings.AWS_REGION
