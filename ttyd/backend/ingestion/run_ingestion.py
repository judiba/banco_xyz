# backend/ingestion/run_ingestion.py

import sys


from .pipeline import run_ingestion
from .registry import mark_ready


def ingest(dataset: str):
    run_ingestion(dataset)

    mark_ready(dataset)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m backend.ingestion.run_ingestion <dataset>")
        sys.exit(1)

    dataset = sys.argv[1]

    ingest(dataset)

    print(f"Ingesting dataset: {dataset}")

# 1. docs
# 2. chunks
# 3. embeddings
# 4. vector store
