from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT / "backend"))

from app.services.rag_service import ensure_vector_store

if __name__ == "__main__":
    ensure_vector_store()
    print("Vector store pronto em data/vector_store")
