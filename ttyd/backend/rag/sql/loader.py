# infra/rag_sql/loader.py

import json
from typing import Any, Dict, List


def load_json_or_jsonl(raw_text: str) -> List[Dict[str, Any]]:
    """
    Carrega JSON ou JSONL e retorna lista de dicts.
    """
    try:
        data = json.loads(raw_text)
        if isinstance(data, dict):
            return [data]
        if isinstance(data, list):
            return data
        raise ValueError("Formato JSON inválido")
    except json.JSONDecodeError:
        # JSONL
        items = []
        for line in raw_text.splitlines():
            line = line.strip()
            if not line:
                continue
            items.append(json.loads(line))
        return items
