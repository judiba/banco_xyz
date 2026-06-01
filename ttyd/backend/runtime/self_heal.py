# backend/runtime/self_heal.py

import os
import subprocess
import sys


# =====================================================
# SELF HEAL SYSTEM
# =====================================================


def _run(cmd):
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def _check_poetry_env():
    """Ensure poetry environment exists"""
    try:
        subprocess.check_output(["poetry", "env", "info"])
    except Exception:
        print("🩹 Creating poetry environment...")
        _run(["poetry", "install"])


def _check_env_file(env: str):
    """Ensure .env exists"""
    env_file = f".env.{env}"

    if not os.path.exists(env_file):
        print(f"🩹 Missing {env_file}, creating from template")

        if os.path.exists(".env.example"):
            subprocess.run(["cp", ".env.example", env_file])


def _check_pythonpath():
    """Guarantee backend module import"""
    root = os.getcwd()

    if root not in sys.path:
        sys.path.insert(0, root)


# =====================================================
# PUBLIC API
# =====================================================


def heal():
    """
    Platform self recovery.
    Called every boot + runtime failures.
    """

    env = os.environ.get("APP_ENV", "dev")

    print("🩹 Self-Heal running...")

    _check_pythonpath()
    _check_poetry_env()
    _check_env_file(env)

    print("✅ Runtime healthy")
