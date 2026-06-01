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

    _log("\n📄 Ambiente de desenvolvimento")
    _log("==============================")
    check_file(ROOT / "security/.env.dev", "Configuração .env.dev")
    check_port(8000)

    _log("\n📄 Ambiente local")
    _log("==============================")
    check_file(ROOT / "security/.env.local", "Configuração .env.local")
    check_port(8000)

    _log("\n📄 Ambiente de produção")
    _log("==============================")
    check_file(ROOT / "security/.env.prod", "Configuração .env.prod")
    check_port(8000)

    _log("\n📁 Verificação de Estrutura de Pastas e Arquivos")
    _log("========================================")
    folders = ["security", "backend/app_config"]
    for f in folders:
        path = ROOT / f
        if path.exists():
            _log(f"✅ Pasta {f}: Encontrada")
        else:
            _log(f"⚠️ Pasta {f}: Ausente")

    files = [
        "backend/app_config/desc_tables.yaml",
        "backend/app_config/desc_colunas.yaml",
        "backend/app_config/descricao.py",
        "tests/backend/services/test_redshift.py",
        "tests/backend/api/test_invoke.py",
        "tests/test_schema_yaml.py",
        "scripts/generate_doctor.py",
        "poetry.lock",
        "README.md",
        "backend/main.py",
    ]
    for f in files:
        path = ROOT / f
        if path.exists():
            _log(f"✅ Arquivo {f}: Encontrado")
        else:
            _log(f"⚠️ Arquivo {f}: Ausente")

    _log("✅ Diagnóstico finalizado.\n")
    _log("Para melhorar a qualidade do ambiente, execute:")
    _log("make flow")
    _log("==============================")


if __name__ == "__main__":
    main()
