# infra/rag_docs/loader/pdf_loader.py

from backend.infrastructure.rag_docs.loader.base import BaseDocumentLoader
from io import BytesIO
from pypdf import PdfReader


class PdfLoader(BaseDocumentLoader):
    def load(self, raw_bytes: bytes) -> str:
        reader = PdfReader(BytesIO(raw_bytes))
        pages = []

        for page in reader.pages:
            text = page.extract_text()
            if text:
                pages.append(text)

        return "\n".join(pages)
