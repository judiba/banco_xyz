import subprocess
import socket
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _log(msg: str):
    print(f"{msg}")


def check_command(cmd: list[str], name: str):
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if result.returncode == 0:
            version = result.stdout.split("\n")[0]
            _log(f"✅ {name}: {version}")
            return True
        else:
            _log(f"❌ {name} não encontrado ou erro ao executar")
            return False
    except FileNotFoundError:
        _log(f"❌ {name} não instalado")
        return False


def check_docker_running():
    try:
        result = subprocess.run(["docker", "info"], capture_output=True, text=True, check=False)
        if result.returncode == 0:
            _log("✅ Docker: Rodando")
            return True
        else:
            _log("❌ Docker: Daemon não está rodando")
            return False
    except FileNotFoundError:
        _log("❌ Docker: Não instalado")
        return False


def check_file(path: Path, name: str):
    if path.exists():
        _log(f"✅ {name}: Encontrado")
        return True
    else:
        _log(f"⚠️ {name}: Ausente")
        return False


def check_port(port: int):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(("127.0.0.1", port))
            _log(f"✅ Porta {port}: Livre")
            return True
        except socket.error:
            _log(f"⚠️ Porta {port}: Ocupada")
            return False


def main():
    _log("\n🩺 TTYD Environment Doctor")
    _log("==============================")

    check_command(["python3", "--version"], "Python")
    check_command(["poetry", "--version"], "Poetry")
    check_command(["docker", "--version"], "Docker CLI")
    check_docker_running()

    check_file(ROOT / "security/.env.dev", "Configuração .env.dev")
    check_port(8000)

    _log("==============================")
    _log("✅ Diagnóstico finalizado.\n")


if __name__ == "__main__":
    main()
