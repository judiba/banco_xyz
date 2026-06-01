import os
import platform


def detect_machine():
    return {
        "os": platform.system(),
        "python": platform.python_version(),
        "cpu": os.cpu_count(),
        "env": os.getenv("APP_ENV", "dev"),
    }
