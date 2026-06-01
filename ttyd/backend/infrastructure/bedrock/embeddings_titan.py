import json
import logging
import numpy as np

from backend.app_config.bedrock import get_bedrock_runtime

logger = logging.getLogger(__name__)

TITAN_EMBED_MODEL_ID = "amazon.titan-embed-text-v2:0"
EMBED_DIM = 1024


def titan_embed(
    text: str,
    dims: int = EMBED_DIM,
    normalize: bool = True,
) -> np.ndarray:
    """
    Gera embedding com Amazon Titan Embed v2 via Bedrock Runtime.

    Retorna:
        np.ndarray (float32) com shape (dims,)
    """
    if not text:
        raise ValueError("Texto para embedding não pode ser vazio.")

    bedrock_rt = get_bedrock_runtime()

    body = json.dumps(
        {
            "inputText": text,
            "dimensions": dims,
            "normalize": normalize,
        }
    )

    logger.debug("Gerando embedding Titan (dims=%s)", dims)

    resp = bedrock_rt.invoke_model(
        modelId=TITAN_EMBED_MODEL_ID,
        body=body,
        accept="application/json",
        contentType="application/json",
    )

    payload = json.loads(resp["body"].read())
    emb = np.array(payload["embedding"], dtype=np.float32)

    return emb
