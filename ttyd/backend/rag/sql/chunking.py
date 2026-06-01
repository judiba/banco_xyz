# infra/rag_sql/chunking.py

from typing import Any, Dict, List


def dict_to_text(d: Dict[str, Any]) -> str:
    """
    Flatten de JSON:
    gera linhas do tipo "chave.subchave: valor"
    """
    lines: List[str] = []

    def _flat(prefix: str, obj: Any):
        if isinstance(obj, dict):
            for k, v in obj.items():
                _flat(f"{prefix}{k}.", v)
        elif isinstance(obj, list):
            for i, v in enumerate(obj):
                _flat(f"{prefix}{i}.", v)
        else:
            lines.append(f"{prefix[:-1]}: {obj}")

    _flat("", d)
    return "\n".join(lines)


def split_chunks(text: str, max_chars: int = 1200) -> List[str]:
    return [text[i : i + max_chars] for i in range(0, len(text), max_chars)]
