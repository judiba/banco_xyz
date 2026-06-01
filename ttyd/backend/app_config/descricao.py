import yaml


def yaml_to_prompt_string(yaml_path: str) -> str:
    with open(yaml_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    linhas = []
    linhas.append("ESQUEMA DO BANCO (Amazon Redshift):\n")

    tabelas = data.get("tabelas", {})

    for nome_tabela, detalhes in tabelas.items():
        linhas.append(f"Tabela: {nome_tabela}")

        descricao = detalhes.get("descricao", "Sem descrição")
        linhas.append("Descrição:")
        linhas.append(f"  {descricao.strip()}")
        linhas.append("")  # linha em branco entre tabelas

    return "\n".join(linhas)
