import importlib
import boto3

from backend.app_config.settings import settings

try:
    strands_models = importlib.import_module("strands.models")
    BedrockModel = getattr(strands_models, "BedrockModel")
except ImportError:
    BedrockModel = None

_session: boto3.Session | None = None
_bedrock_model = None
_bedrock_runtime = None
_s3_client = None


def get_aws_session() -> boto3.Session:
    global _session

    if _session is None:
        if settings.APP_ENV == "local" and settings.AWS_PROFILE:
            _session = boto3.Session(
                profile_name=settings.AWS_PROFILE,
                region_name=settings.AWS_REGION,
            )
        else:
            _session = boto3.Session(region_name=settings.AWS_REGION)

    return _session


def create_bedrock_model():
    global _bedrock_model

    if BedrockModel is None:
        raise RuntimeError("strands não instalado. Instale com: pip install strands-agents")

    if _bedrock_model is None:
        _bedrock_model = BedrockModel(
            model_id=settings.LLM_MODEL,
            boto_session=get_aws_session(),
            temperature=0.1,
            top_p=0.8,
            max_tokens=2048,
        )

    return _bedrock_model


def get_bedrock_model():
    return create_bedrock_model()


def get_bedrock_runtime():
    global _bedrock_runtime

    if _bedrock_runtime is None:
        _bedrock_runtime = get_aws_session().client("bedrock-runtime")

    return _bedrock_runtime


def get_s3_client():
    global _s3_client

    if _s3_client is None:
        _s3_client = get_aws_session().client("s3")

    return _s3_client
