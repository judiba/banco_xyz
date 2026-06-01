import importlib
import os
import subprocess
import sys


CHECKS = [
    ("uvicorn", "uvicorn"),
    ("fastapi", "fastapi"),
    ("langchain", "langchain"),
    ("langchain_community", "langchain_community"),
    ("boto3", "boto3"),
]


def check_python():
    print("🐍 Python:", sys.version)


def check_env():
    env = os.getenv("APP_ENV", "not-set")
    print("🌎 Environment:", env)


def check_imports():
    print("\n📦 Checking imports...")
    missing = []

    for name, module in CHECKS:
        try:
            importlib.import_module(module)
            print(f"✅ {name}")
        except Exception:
            print(f"❌ Missing: {name}")
            missing.append(name)

    return missing


def check_structure():
    print("\n📁 Checking folders...")

    folders = ["logs", "data", "vectorstore"]

    for f in folders:
        if not os.path.exists(f):
            print(f"⚠️ creating {f}")
            os.makedirs(f, exist_ok=True)
        else:
            print(f"✅ {f}")


def auto_fix(packages):
    if not packages:
        return

    print("\n♻️ Auto-install missing packages...")
    subprocess.run(
        ["poetry", "add", *packages],
        check=False,
    )


def run():
    print("\n🩺 Agent Runtime Doctor\n")

    check_python()
    check_env()

    missing = check_imports()

    check_structure()

    auto_fix(missing)

    print("\n✅ Doctor finished\n")


if __name__ == "__main__":
    run()
