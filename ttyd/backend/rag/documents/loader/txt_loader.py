# infra/rag_docs/loader/txt_loader.py
from backend.infrastructure.rag_docs.loader.base import BaseDocumentLoader


class TxtLoader(BaseDocumentLoader):
    def load(self, raw_bytes: bytes) -> str:
        return raw_bytes.decode("utf-8")
