from pathlib import Path

from app.core.config import REPORTS_DIR


def validate_report_path(path: str) -> Path:
    candidate = Path(path).resolve()
    reports_dir = REPORTS_DIR.resolve()

    if reports_dir not in candidate.parents and candidate != reports_dir:
        raise ValueError("Caminho de arquivo inválido")

    if not candidate.exists():
        raise ValueError("Arquivo não encontrado")

    return candidate
