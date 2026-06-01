import json
from pathlib import Path
from backend.core.storage import tenant_path


def registry_file(ctx):
    return tenant_path(ctx.namespace) / "dataset.json"


def mark_tenant_ready(ctx):
    registry_file(ctx).write_text(json.dumps({"status": "READY"}))


def tenant_ready(ctx):
    f = registry_file(ctx)

    if not f.exists():
        return False

    return json.loads(f.read_text())["status"] == "READY"


REGISTRY_FILE = Path("backend/dev_data/dataset_registry.json")


def mark_ready(dataset: str):
    data = {}

    if REGISTRY_FILE.exists():
        data = json.loads(REGISTRY_FILE.read_text())

    data[dataset] = {"status": "READY"}

    REGISTRY_FILE.write_text(json.dumps(data, indent=2))


def dataset_ready(dataset: str) -> bool:
    if not REGISTRY_FILE.exists():
        return False

    data = json.loads(REGISTRY_FILE.read_text())

    return data.get(dataset, {}).get("status") == "READY"
