# scripts/validate_yaml_quality.py
try:
    import yaml
except ImportError:
    raise SystemExit("PyYAML não instalado. Execute: poetry add pyyaml")
from pathlib import Path
import sys

# Mapeia os caminhos baseados na estrutura do projeto
ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = ROOT / "backend" / "app_config"
TABLES_YAML = CONFIG_DIR / "desc_tables.yaml"
COLUMNS_YAML = CONFIG_DIR / "desc_colunas.yaml"

MIN_DESCRIPTION_LENGTH = 15  # Comprimento mínimo aceitável para o prompt da LLM


def find_line_number(file_path: Path, search_key: str, sub_key: str | None = None) -> int:
    if not file_path.exists():
        return 1
    """Busca a linha aproximada do termo no arquivo para facilitar o debug."""
    try:
        lines = file_path.read_text(encoding="utf-8").splitlines()
        for idx, line in enumerate(lines):
            if f"{search_key}:" in line:
                if not sub_key:
                    return idx + 1
                # Se houver uma subchave (ex: coluna dentro da tabela), busca a partir dali
                for sub_idx, sub_line in enumerate(lines[idx:]):
                    if f"{sub_key}:" in sub_line:
                        return idx + sub_idx + 1
    except Exception:
        pass
    return 1


def validate_quality() -> bool:
    has_errors = False
    print("🔍 [LEVEL 19] Iniciando varredura de qualidade dos metadados da LLM...")

    # --- VALIDAR DESC_TABLES.YAML ---
    if TABLES_YAML.exists():
        with open(TABLES_YAML, "r", encoding="utf-8") as f:
            tables_data = yaml.safe_load(f) or {}

        tabelas = tables_data.get("tabelas", {})
        for tab_nome, tab_info in tabelas.items():
            desc = tab_info.get("descricao", "").strip()
            if len(desc) < MIN_DESCRIPTION_LENGTH:
                line = find_line_number(TABLES_YAML, tab_nome)
                print(
                    f"⚠️  [desc_tables.yaml:{line}] Tabela '{tab_nome}' possui descrição muito curta ({len(desc)} caracteres). Enriqueça o contexto de negócio."
                )
                has_errors = True
    else:
        print(f"❌ Arquivo não encontrado: {TABLES_YAML}")
        has_errors = True

    # --- VALIDAR DESC_COLUNAS.YAML ---
    if COLUMNS_YAML.exists():
        with open(COLUMNS_YAML, "r", encoding="utf-8") as f:
            columns_data = yaml.safe_load(f) or {}

        tabelas_col = columns_data.get("tabelas", {})
        for tab_nome, tab_info in tabelas_col.items():
            colunas = tab_info.get("colunas", [])
            for col in colunas:
                col_nome = col.get("nome", "")
                desc = col.get("descricao", "").strip()

                # Regra A: Tamanho da descrição
                if len(desc) < MIN_DESCRIPTION_LENGTH:
                    line = find_line_number(COLUMNS_YAML, tab_nome, col_nome)
                    print(
                        f"⚠️  [desc_colunas.yaml:{line}] Coluna '{col_nome}' da tabela '{tab_nome}' precisa de mais detalhes funcionais."
                    )
                    has_errors = True

                # Regra B: Verificação de Flags Binárias (is_, tem_, possui_)
                if any(
                    col_nome.lower().startswith(p) for p in ["is_", "has_", "tem_", "flag_", "ind_"]
                ):
                    if not any(
                        x in desc.lower() for x in ["0", "1", "sim", "não", "true", "false"]
                    ):
                        line = find_line_number(COLUMNS_YAML, tab_nome, col_nome)
                        print(
                            f"💡 [desc_colunas.yaml:{line}] Coluna binária '{col_nome}' em '{tab_nome}' não especifica o significado dos valores (ex: 1=Sim, 0=Não)."
                        )
                        # Apenas um aviso (Warning), não marca has_errors = True para não travar o build por isso
    else:
        print(f"❌ Arquivo não encontrado: {COLUMNS_YAML}")
        has_errors = True

    if has_errors:
        print("\n❌ Falha nos critérios mínimos de qualidade para produção.")
        return False

    print("\n✅ Todos os arquivos YAML possuem riqueza de contexto aprovada para a LLM!")
    return True


if __name__ == "__main__":
    success = validate_quality()
    # Se houver erros de qualidade crítica, encerra com código 1 para travar o Makefile/Pipeline
    sys.exit(0 if success else 1)
