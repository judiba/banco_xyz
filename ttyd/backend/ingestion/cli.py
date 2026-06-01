import sys
from .run_ingestion import ingest

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m backend.ingestion.cli <dataset>")
        sys.exit(1)

    dataset = sys.argv[1]

    ingest(dataset)
