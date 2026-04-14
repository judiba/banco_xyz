from __future__ import annotations

from pathlib import Path
import docker

ROOT = Path(__file__).resolve().parents[1]
client = docker.from_env()


def build_image(tag: str, path: Path):
    print(f"Construindo {tag} a partir de {path}...")
    image, logs = client.images.build(path=str(path), tag=tag)
    for chunk in logs:
        if "stream" in chunk:
            print(chunk["stream"], end="")
    print(f"Imagem pronta: {image.tags}")


if __name__ == "__main__":
    build_image("banco_xyz_backend_sdk:latest", ROOT / "backend")
    build_image("banco_xyz_frontend_sdk:latest", ROOT / "frontend")
