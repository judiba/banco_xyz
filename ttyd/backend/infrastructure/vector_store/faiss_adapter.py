import faiss
import numpy as np
import logging
from typing import List, Dict, Any

from backend.infrastructure.bedrock.embeddings_titan import titan_embed

logger = logging.getLogger(__name__)


class FaissRAGIndex:
    def __init__(self, dim: int = 1024):
        # IP + vetores normalizados = cosine
        self.index = faiss.IndexFlatIP(dim)
        self.texts: List[str] = []
        self.meta: List[Dict[str, Any]] = []
        self.vecs: np.ndarray | None = None

    def add(self, vectors: np.ndarray, texts: List[str], metas: List[Dict[str, Any]]):
        assert vectors.shape[0] == len(texts) == len(metas)

        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        vectors = vectors / np.clip(norms, 1e-12, None)

        self.index.add(vectors)
        self.texts.extend(texts)
        self.meta.extend(metas)

    def search(self, query: str, k: int = 5):
        q = titan_embed(query)
        q = q / np.clip(np.linalg.norm(q), 1e-12, None)

        distances, indices = self.index.search(q.reshape(1, -1), k)

        hits = []
        for score, idx in zip(distances[0].tolist(), indices[0].tolist()):
            if idx == -1:
                continue
            hits.append(
                {
                    "score": score,
                    "text": self.texts[idx],
                    "meta": self.meta[idx],
                }
            )
        return hits
