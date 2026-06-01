from pathlib import Path


BASE = Path("runtime_data")


def tenant_path(namespace: str):
    path = BASE / namespace
    path.mkdir(parents=True, exist_ok=True)

    return path
