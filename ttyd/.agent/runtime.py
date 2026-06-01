import subprocess
import os


def start_runtime():
    env = os.getenv("APP_ENV", "dev")

    print(f"🧠 Agent starting runtime ({env})")

    if env in ("dev", "local"):
        subprocess.run(["poetry", "run", "python", "-m", "backend.runtime.bootstrap"])

    else:
        subprocess.run(["poetry", "run", "python", "backend/agents/agentcore_runtime.py"])
