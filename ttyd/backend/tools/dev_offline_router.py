from pathlib import Path
import json


BASE_DIR = Path(__file__).resolve().parent.parent
DEV_DATA_DIR = BASE_DIR / "dev_data"


def _load_json(filename: str):
    with open(DEV_DATA_DIR / filename, "r", encoding="utf-8") as f:
        return json.load(f)


def handle_offline_query(user_query: str):
    query = (user_query or "").lower().strip()

    users = _load_json("mock_users.json")
    sales = _load_json("mock_sales.json")
    metrics = _load_json("mock_metrics.json")
    docs = _load_json("docs.json")

    # -----------------------------
    # Consultas analíticas
    # -----------------------------
    if "receita" in query or "faturamento" in query:
        return {
            "status": "success",
            "result": {
                "columns": ["mes", "receita", "ticket_medio"],
                "rows": [[x["mes"], x["receita"], x["ticket_medio"]] for x in sales],
                "summary": "Evolução mensal de receita e ticket médio.",
            },
        }

    if "pedido" in query:
        return {
            "status": "success",
            "result": {
                "columns": ["mes", "pedidos"],
                "rows": [[x["mes"], x["pedidos"]] for x in sales],
                "summary": "Volume mensal de pedidos.",
            },
        }

    if "usuário" in query or "usuarios" in query or "usuários" in query:
        return {
            "status": "success",
            "result": {
                "columns": ["mes", "usuarios_ativos", "novos_usuarios", "churn"],
                "rows": [
                    [x["mes"], x["usuarios_ativos"], x["novos_usuarios"], x["churn"]] for x in users
                ],
                "summary": "Evolução mensal de usuários ativos, novos usuários e churn.",
            },
        }

    if "canal" in query or "convers" in query or "lead" in query:
        return {
            "status": "success",
            "result": {
                "columns": ["canal", "leads", "conversoes", "taxa_conversao"],
                "rows": [
                    [x["canal"], x["leads"], x["conversoes"], x["taxa_conversao"]] for x in metrics
                ],
                "summary": "Performance por canal de aquisição.",
            },
        }

    # -----------------------------
    # Consultas documentais
    # -----------------------------
    if (
        "política" in query
        or "politica" in query
        or "segurança" in query
        or "governança" in query
        or "governanca" in query
    ):
        trechos = []
        for doc in docs[:3]:
            trechos.append(f"**{doc['titulo']}**\n{doc['texto']}")

        return {
            "status": "success",
            "result": {
                "columns": ["conteudo"],
                "rows": [[t] for t in trechos],
                "summary": "Trechos relevantes das políticas internas.",
            },
        }

    # -----------------------------
    # Fallback
    # -----------------------------
    return {
        "status": "success",
        "result": {
            "columns": ["mensagem"],
            "rows": [
                [
                    "Não encontrei um mock específico para essa pergunta.\n\n"
                    "Tente algo como:\n"
                    "- qual a receita por mês?\n"
                    "- quantos pedidos tivemos?\n"
                    "- qual canal converte mais?\n"
                    "- como estão os usuários ativos?"
                ]
            ],
            "summary": "Resposta padrão do ambiente offline.",
        },
    }
