import faiss
import numpy as np
from typing import Any


class FaissRAGSQLIndex:
    """
    Índice FAISS para contexto auxiliar de Text-to-SQL.
    """

    def __init__(self, dim: int):
        self.index: Any = faiss.IndexFlatIP(dim)
        self.texts: list[str] = []
        self.meta: list[dict[str, Any]] = []

    def add(
        self,
        vectors: np.ndarray,
        texts: list[str],
        meta: list[dict[str, Any]],
    ):
        assert vectors.shape[0] == len(texts) == len(meta)

        vectors = vectors.astype("float32")
        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        vectors = vectors / np.clip(norms, 1e-12, None)

        self.index.add(vectors)
        self.texts.extend(texts)
        self.meta.extend(meta)

    def search(self, query_vec: np.ndarray, k: int = 5):
        query_vec = query_vec.astype("float32")
        query_vec = query_vec.reshape(1, -1)

        distances, indices = self.index.search(query_vec, k)

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
