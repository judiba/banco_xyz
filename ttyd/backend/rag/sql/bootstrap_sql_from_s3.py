import json
from pathlib import Path
from backend.app_config.settings import settings


def bootstrap_sql_from_s3(bucket: str, key: str):
    if settings.DEV_OFFLINE:
        print("🧪 DEV OFFLINE: carregando RAG SQL local")
        path = Path(__file__).resolve().parent.parent.parent / "dev_data" / "sql.json"

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        print(f"Loaded {len(data)} SQL entries (local)")
        return data

    raise NotImplementedError("S3 bootstrap não configurado no modo real ainda")
