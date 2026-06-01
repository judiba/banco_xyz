# infra/embedding.py

import json
import numpy as np
from backend.app_config.bedrock import get_bedrock_runtime

TITAN_EMBED_MODEL_ID = "amazon.titan-embed-text-v2:0"
EMBED_DIM = 1024


def titan_embed(
    text: str,
    dims: int = EMBED_DIM,
    normalize: bool = True,
) -> np.ndarray:
    """
    Gera embedding usando Titan v2 (Bedrock Runtime).
    """
    bedrock_rt = get_bedrock_runtime()

    body = json.dumps(
        {
            "inputText": text,
            "dimensions": dims,
            "normalize": normalize,
        }
    )

    resp = bedrock_rt.invoke_model(
        modelId=TITAN_EMBED_MODEL_ID,
        body=body,
        accept="application/json",
        contentType="application/json",
    )

    payload = json.loads(resp["body"].read())
    emb = np.array(payload["embedding"], dtype=np.float32)
    return emb
