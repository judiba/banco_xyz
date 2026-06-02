from backend.ingestion.registry import dataset_ready


def validate_dataset(dataset="default"):
    if not dataset_ready(dataset):
        raise RuntimeError("Dataset not ingested. Run: ./dev ingest")
