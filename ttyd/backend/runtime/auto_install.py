import subprocess
import shutil


def poetry_exists():
    return shutil.which("poetry") is not None


def ensure_poetry():
    if poetry_exists():
        return

    print("⚙️ Installing Poetry automatically...")
    subprocess.run(
        "curl -sSL https://install.python-poetry.org | python3 -",
        shell=True,
        check=True,
    )


def deps_installed():
    try:
        subprocess.run(
            ["poetry", "run", "python", "-c", "import fastapi"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
        )
        return True
    except Exception:
        return False


def install_environment(env: str):
    print(f"📦 Installing dependencies for [{env}] environment")

    groups = {
        "dev": "dev",
        "local": "local",
        "prod": "prod,bedrock",
    }

    subprocess.run(
        ["poetry", "install", "--with", groups[env]],
        check=True,
    )


def ensure_runtime(env: str):
    ensure_poetry()

    if not deps_installed():
        install_environment(env)
