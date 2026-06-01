from pathlib import Path
from string import Template
from datetime import datetime

ROOT = Path(__file__).resolve().parent.parent

TEMPLATE_PATH = ROOT / "README.template.md"
OUTPUT_PATH = ROOT / "README.md"

PROJECT_CONTEXT = {
    "project_name": "TTYD — Talk To Your Data",
    "project_description": "**TTYD — Talk To Your Data** is a Platform for Data Science and Analytics",
    "organization": "NTT DATA",
    "logo": "https://avatars.githubusercontent.com/u/10359443?s=200&v=4",
    "objective": "**TTYD (Talk To Your Data)** é uma plataforma de consulta inteligente baseada em agentes:",
    "project_level": "19",
    "python_version": "3.12+",
    "project_status": "Observability & Tracing",
    "project_status_badge": "Observability_&_Tracing",
    "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "author": "NTTData Squad Estratégia Digital e CRM",
    "version": "19.0.0",
    "license": "Projeto interno NTT DATA / Record. Consulte o time responsável pelo repositório para políticas de uso e contribuição.",
    "logo_gitlab": "https://avatars.githubusercontent.com/u/10359443?s=200&v=4",
    "repo": "https://git-ssh.emeal.nttdata.com/DATASCIENC/talktoyourdata.git",
    "repo_ssh": "ssh://git@git-ssh.emeal.nttdata.com:766/DATASCIENC/talktoyourdata.git",
    "repo_name": "talktoyourdata",
    "repo_branch": "main",
    "branch": "feature/ttyd",
    "repo_commit": "HEAD",
    "repo_commit_short": "HEAD",
    "repo_commit_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "repo_commit_hash": "HEAD",
}


def load_template() -> Template:
    if not TEMPLATE_PATH.exists():
        raise FileNotFoundError(f"Template não encontrado: {TEMPLATE_PATH}")

    content = TEMPLATE_PATH.read_text(encoding="utf-8")
    return Template(content)


def generate_readme() -> None:
    template = load_template()
    rendered = template.safe_substitute(PROJECT_CONTEXT)

    OUTPUT_PATH.write_text(rendered, encoding="utf-8")
    print(f"✅ README.md gerado com sucesso: {OUTPUT_PATH}")


def main() -> None:
    generate_readme()


if __name__ == "__main__":
    main()
