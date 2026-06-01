"""
SELF HEALING RUNTIME
talktoyourdata Platform

Auto-repairs environment before boot.
"""

import subprocess
import importlib
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]


# ======================================================
# UTILS
# ======================================================


def _log(msg: str):
    print(f"🧠 [SELF-HEAL] {msg}")


def _run(cmd: list[str]):
    subprocess.run(cmd, check=False)


# ======================================================
# CHECKS
# ======================================================


def check_module(module: str):
    try:
        importlib.import_module(module)
        _log(f"module ok → {module}")
        return True
    except Exception:
        _log(f"missing module → {module}")
        return False


def install_dependencies():
    _log("installing dependencies via poetry...")
    _run(["poetry", "install"])


def fix_python_path():
    root = str(PROJECT_ROOT)

    if root not in sys.path:
        sys.path.insert(0, root)
        _log("PYTHONPATH repaired")


def ensure_init_files():
    """
    Guarantee Python packages exist.
    """
    for path in PROJECT_ROOT.rglob("*"):
        if path.is_dir():
            init = path / "__init__.py"
            if not init.exists():
                init.touch()


def validate_orchestrator():
    try:
        from backend.agents.orchestrator import get_orchestrator

        orch = get_orchestrator()

        if orch is None:
            raise RuntimeError("Orchestrator returned None")

        _log("orchestrator ready")

    except Exception as e:
        _log(f"orchestrator failure → {e}")
        raise


def clear_pycache():
    _log("clearing __pycache__")

    for p in PROJECT_ROOT.rglob("__pycache__"):
        try:
            for f in p.iterdir():
                f.unlink()
            p.rmdir()
        except Exception:
            pass


# ======================================================
# MAIN HEALING PIPELINE
# ======================================================


def heal():
    _log("starting self-healing sequence")

    fix_python_path()
    ensure_init_files()

    if not check_module("uvicorn"):
        install_dependencies()

    clear_pycache()

    validate_orchestrator()

    _log("self-healing completed ✅")


# ======================================================
# ENTRYPOINT
# ======================================================

if __name__ == "__main__":
    heal()
