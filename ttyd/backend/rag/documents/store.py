import faiss
import numpy as np
from typing import List, Dict, Any

from backend.ingestion.embedding import titan_embed


class FaissRAGDocsIndex:
    def __init__(self, dim: int = 1024):
        self.index = faiss.IndexFlatIP(dim)
        self.texts: List[str] = []
        self.meta: List[Dict[str, Any]] = []

    def add(self, vectors: np.ndarray, texts: List[str], file_id: str):
        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        vectors = vectors / np.clip(norms, 1e-12, None)

        self.index.add(vectors)

        for i, txt in enumerate(texts):
            self.texts.append(txt)
            self.meta.append({"file_id": file_id, "chunk_id": i})

    def search(self, query: str, k: int = 5):
        q = titan_embed(query)
        q = q / np.clip(np.linalg.norm(q), 1e-12, None)

        distances, indices = self.index.search(q.reshape(1, -1), k)

        hits = []
        for score, idx in zip(distances[0], indices[0]):
            if idx == -1:
                continue
            hits.append(
                {
                    "score": float(score),
                    "text": self.texts[idx],
                    "meta": self.meta[idx],
                }
            )
        return hits
