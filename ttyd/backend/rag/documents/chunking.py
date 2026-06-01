from typing import List


def split_chunks(text: str, max_chars: int = 1200) -> List[str]:
    """
    Divide texto longo em chunks menores para embedding.
    """
    text = text.strip()
    if not text:
        return []

    return [text[i : i + max_chars] for i in range(0, len(text), max_chars)]
