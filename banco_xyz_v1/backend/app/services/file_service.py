from __future__ import annotations

from pathlib import Path

from app.core.security import validate_report_path



def resolve_report_file(path: str) -> Path:
    return validate_report_path(path)
