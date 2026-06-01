import boto3
import pandas as pd
import io
from datetime import datetime
from backend.core.tenant import TenantContext
from backend.infrastructure.rag_docs.loader.dispatcher import load_documents
from backend.infrastructure.rag_docs.chunking import chunk_documents
from backend.ingestion.embedding import generate_embeddings
from backend.infrastructure.rag_docs.store import store_vectors


def run_ingestion(org_id: str, dataset: str):
    ctx = TenantContext(org_id=org_id, dataset=dataset)

    docs = load_documents(ctx)

    chunks = chunk_documents(docs)

    vectors = generate_embeddings(ctx, chunks)

    store_vectors(ctx, ctx, vectors)

    print("[INGESTION] completed")


# TO DO: Refatorar para usar o pipeline de ingestão genérico, que pode ser adaptado para diferentes fontes de dados (ex: S3, APIs, bancos de dados). O código atual é um exemplo específico para ingestão de arquivos CSV para o S3, mas a ideia é criar uma estrutura mais flexível e reutilizável.

# Configurações do S3
BUCKET_NAME = "nome-do-seu-bucket"
S3_FOLDER = "raw-data"
LOCAL_FILE = "dados.csv"


def ingest_data_to_s3():
    # 1. Extração: Lendo dados (ex: CSV local)
    try:
        df = pd.read_csv(LOCAL_FILE)
        print("Dados lidos com sucesso.")
    except Exception as e:
        print(f"Erro ao ler arquivo: {e}")
        return

    # 2. Transformação: Opcional (Limpeza, conversão de tipos)
    # Ex: Adicionar timestamp de ingestão
    df["ingested_at"] = datetime.now()

    # 3. Carga: Preparando para o S3
    s3_client = boto3.client("s3")

    # Converte o DataFrame para CSV/Parquet em memória
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)

    file_name = f"{S3_FOLDER}/data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

    # 4. Upload com Boto3
    try:
        s3_client.put_object(Bucket=BUCKET_NAME, Key=file_name, Body=csv_buffer.getvalue())
        print(f"Arquivo {file_name} carregado com sucesso no S3.")
    except Exception as e:
        print(f"Erro no upload para S3: {e}")


if __name__ == "__main__":
    ingest_data_to_s3()
