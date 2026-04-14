from app.services.rag_service import ensure_vector_store

try:
    ensure_vector_store()
    print("Vector store inicializado com sucesso.")
except Exception as e:
    print(f"Falha ao inicializar vector store: {e}")