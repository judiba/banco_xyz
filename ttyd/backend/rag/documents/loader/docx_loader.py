from backend.rag.documents.loader.base import BaseDocumentLoader
from io import BytesIO
from docx import Document


class DocxLoader(BaseDocumentLoader):
    def load(self, raw_bytes: bytes) -> str:
        doc = Document(BytesIO(raw_bytes))
        return "\n".join(p.text for p in doc.paragraphs if p.text)
