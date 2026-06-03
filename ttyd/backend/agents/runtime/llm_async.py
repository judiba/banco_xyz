import json

import aioboto3
from backend.config import get_config


async def generate(ctx):
    cfg = get_config()
    async with aioboto3.Session(region_name=cfg.aws_region).client(
        "bedrock-runtime"
    ) as client:
        response = await client.invoke_model(
            body=json.dumps(
                {
                    "prompt": ctx.question,
                    "max_tokens": 1000,
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "top_k": 40,
                    "stop_sequences": ["\n\n\n"],
                }
            ),
            model_id="amazon.nova-pro-v1:0",
            accept="application/json",
            content_type="application/json",
        )
        response = json.loads(response["body"].read())
        return response["results"][0]["output"]


__all__ = ["generate"]
