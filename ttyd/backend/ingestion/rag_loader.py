import json
from typing import List, Dict, Any
from backend.infrastructure.bedrock import get_s3_client

s3 = get_s3_client()


def load_s3_json_or_jsonl(bucket: str, key: str) -> List[Dict[str, Any]]:
    obj = s3.get_object(Bucket=bucket, Key=key)
    raw = obj["Body"].read().decode("utf-8")

    try:
        data = json.loads(raw)
        return data if isinstance(data, list) else [data]
    except json.JSONDecodeError:
        return [json.loads(line) for line in raw.splitlines() if line.strip()]
