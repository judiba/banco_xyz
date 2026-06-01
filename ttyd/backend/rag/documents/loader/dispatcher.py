from backend.infrastructure.rag_docs.loader.txt_loader import TxtLoader
from backend.infrastructure.rag_docs.loader.pdf_loader import PdfLoader
from backend.infrastructure.rag_docs.loader.docx_loader import DocxLoader


def get_loader(key: str):
    key = key.lower()

    if key.endswith(".txt"):
        return TxtLoader()

    if key.endswith(".pdf"):
        return PdfLoader()

    if key.endswith(".docx"):
        return DocxLoader()

    raise ValueError(f"Formato não suportado: {key}")
