import json
import boto3
from pathlib import Path
from backend.app_config.settings import settings


def bootstrap_docs_from_s3(bucket: str, prefix: str):
    if settings.DEV_OFFLINE:
        print("🧪 DEV OFFLINE: carregando RAG docs local")
        path = Path(__file__).resolve().parent.parent.parent / "dev_data" / "docs.json"

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        print(f"Loaded {len(data)} docs (local)")
        return data

    s3 = boto3.client("s3")

    objects = s3.list_objects_v2(Bucket=bucket, Prefix=prefix)

    for obj in objects.get("Contents", []):
        print(f"Downloading {obj['Key']}")
