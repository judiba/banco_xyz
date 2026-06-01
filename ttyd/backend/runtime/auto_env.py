import os
from pathlib import Path


def running_in_docker():
    return Path("/.dockerenv").exists()


def aws_available():
    return os.getenv("AWS_ACCESS_KEY_ID") or Path.home().joinpath(".aws").exists()


def agentcore_available():
    return os.getenv("AGENTCORE_RUNTIME") == "true"


def detect_environment():
    # 1️⃣ AgentCore sempre ganha
    if agentcore_available():
        return "prod"

    # 2️⃣ AWS real
    if aws_available():
        return "local"

    # 3️⃣ fallback offline
    if running_in_docker():
        return "dev"

    return "dev"
