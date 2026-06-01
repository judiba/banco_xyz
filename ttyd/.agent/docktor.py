import sys
import subprocess
from .constraints import REQUIRED_PYTHON, REQUIRED_PACKAGES


def check_python():
    if sys.version_info < REQUIRED_PYTHON:
        raise RuntimeError(f"Python {REQUIRED_PYTHON}+ required")


def check_packages():
    missing = []

    for pkg in REQUIRED_PACKAGES:
        try:
            __import__(pkg)
        except ImportError:
            missing.append(pkg)

    return missing


def run_doctor():
    print("🩺 Agent Doctor running...")

    check_python()

    missing = check_packages()

    if missing:
        print("⚠ Missing packages:", missing)
        subprocess.run(["poetry", "add", *missing])
    else:
        print("✅ Environment healthy")
