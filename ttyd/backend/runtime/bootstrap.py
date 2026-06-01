import os
import sys
import subprocess

from backend.runtime.auto_env import detect_environment
from backend.runtime.auto_install import ensure_runtime
from backend.runtime.self_heal import heal  # ⭐ garante que o sistema pode existir
from backend.infrastructure.aws.s3 import S3Storage


def bootstrap():
    s3 = S3Storage()

    s3.download(
        bucket="my-bucket",
        key="data/file.parquet",
        target="/tmp/file.parquet",
    )

    print("Runtime ready")


# =====================================================
# ENV DETECTION
# =====================================================

env = detect_environment()

print(f"\n🚀 Auto-Agent selected environment: {env}\n")

os.environ["APP_ENV"] = env


# =====================================================
# SELF HEAL FIRST
# =====================================================

heal()  # ⭐ garante que o sistema pode existir


# =====================================================
# AUTO INSTALL
# =====================================================

ensure_runtime(env)


# =====================================================
# PROCESS LAUNCH
# =====================================================

python = sys.executable


def run(cmd):
    subprocess.run(cmd, check=True)


if env == "dev":
    run([python, "-m", "uvicorn", "backend.main:app", "--reload", "--port", "8080"])

elif env == "local":
    run([python, "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8080"])

elif env == "prod":
    run([python, "-m", "backend.agents.agentcore_runtime"])
