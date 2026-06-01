import faiss
import time
import logging
import numpy as np

from backend.infrastructure.vector_store.faiss_adapter import FaissRAGIndex
from backend.ingestion.rag_loader import load_s3_json_or_jsonl
from backend.ingestion.rag_chunking import split_chunks, dict_to_text
from backend.infrastructure.bedrock.embeddings_titan import titan_embed
from backend.core.storage import tenant_path


def store_vectors(ctx, context, index):
    path = tenant_path(context.namespace)

    index_path = path / "faiss.index"

    faiss.write_index(index, str(index_path))


logger = logging.getLogger(__name__)

_rag_index = None


def get_rag_index() -> FaissRAGIndex:
    global _rag_index
    if _rag_index is None:
        _rag_index = FaissRAGIndex()
    return _rag_index


def build_rag_index_from_s3(
    bucket: str,
    key: str,
    max_chars: int = 1200,
    force: bool = False,
):
    rag_index = get_rag_index()

    if rag_index.index.ntotal > 0 and not force:
        logger.info("RAG já inicializado (ntotal=%d)", rag_index.index.ntotal)
        return rag_index.index.ntotal

    data = load_s3_json_or_jsonl(bucket, key)
    start = time.time()
    total_chunks = 0

    for i, item in enumerate(data):
        text = dict_to_text(item)
        chunks = split_chunks(text, max_chars)
        if not chunks:
            continue

        vectors = np.vstack([titan_embed(c) for c in chunks])
        metas = [{"doc_id": i, "chunk_id": j} for j in range(len(chunks))]

        rag_index.add(vectors, chunks, metas)
        total_chunks += len(chunks)

    logger.info(
        "RAG pronto: docs=%d chunks=%d tempo=%.1fs",
        len(data),
        total_chunks,
        time.time() - start,
    )

    return total_chunks
