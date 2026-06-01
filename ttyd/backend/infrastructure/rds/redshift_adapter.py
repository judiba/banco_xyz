import json
import logging
from pathlib import Path
from typing import Dict, Any

from backend.app_config.settings import settings
from backend.app_config.bedrock import get_aws_session

logger = logging.getLogger(__name__)


def _get_lambda_client():
    session = get_aws_session()
    return session.client("lambda", region_name=settings.AWS_REGION)


def _load_json_file(filename: str):
    base_dir = Path(__file__).resolve().parent.parent / "dev_data"
    file_path = base_dir / filename

    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def _mock_sql_result(sql: str) -> Dict[str, Any]:
    sql_lower = sql.lower()

    users = _load_json_file("mock_users.json")
    sales = _load_json_file("mock_sales.json")
    metrics = _load_json_file("mock_metrics.json")

    if "count" in sql_lower and ("usuario" in sql_lower or "user" in sql_lower):
        total = users[-1]["usuarios_ativos"]
        return {
            "columns": ["usuarios_ativos"],
            "rows": [[total]],
            "summary": f"Total de usuários ativos no último mês: {total}",
        }

    if "usuarios_ativos" in sql_lower:
        return {
            "columns": ["mes", "usuarios_ativos", "novos_usuarios", "churn"],
            "rows": [
                [x["mes"], x["usuarios_ativos"], x["novos_usuarios"], x["churn"]] for x in users
            ],
            "summary": "Evolução mensal de usuários ativos, novos usuários e churn.",
        }

    if "receita" in sql_lower or "faturamento" in sql_lower:
        return {
            "columns": ["mes", "receita", "ticket_medio"],
            "rows": [[x["mes"], x["receita"], x["ticket_medio"]] for x in sales],
            "summary": "Evolução mensal de receita e ticket médio.",
        }

    if "pedido" in sql_lower:
        return {
            "columns": ["mes", "pedidos"],
            "rows": [[x["mes"], x["pedidos"]] for x in sales],
            "summary": "Volume mensal de pedidos.",
        }

    if "convers" in sql_lower or "canal" in sql_lower or "lead" in sql_lower:
        return {
            "columns": ["canal", "leads", "conversoes", "taxa_conversao"],
            "rows": [
                [x["canal"], x["leads"], x["conversoes"], x["taxa_conversao"]] for x in metrics
            ],
            "summary": "Performance por canal de aquisição.",
        }

    if "ticket_medio" in sql_lower:
        return {
            "columns": ["mes", "ticket_medio"],
            "rows": [[x["mes"], x["ticket_medio"]] for x in sales],
            "summary": "Evolução do ticket médio.",
        }

    return {
        "columns": ["mensagem"],
        "rows": [["Mock SQL executado com sucesso"]],
        "summary": "Resultado genérico do ambiente offline.",
    }


def _invoke_redshift_lambda(payload: Dict[str, Any]) -> Dict[str, Any]:
    if not settings.REDSHIFT_LAMBDA_ARN:
        return {
            "status": "error",
            "message": "REDSHIFT_LAMBDA_ARN não configurado no runtime do AgentCore.",
        }

    try:
        client = _get_lambda_client()

        resp = client.invoke(
            FunctionName=settings.REDSHIFT_LAMBDA_ARN,
            InvocationType="RequestResponse",
            Payload=json.dumps(payload).encode("utf-8"),
        )

        raw = resp["Payload"].read()
        data = json.loads(raw)

        status = data.get("statusCode")
        body = data.get("body")

        if status and int(status) >= 400:
            try:
                err = json.loads(body) if isinstance(body, str) else body
            except Exception:
                err = {"error": body}

            return {
                "status": "error",
                "lambda_error": err,
            }

        if isinstance(body, str):
            return json.loads(body)

        return body if body is not None else data

    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "error_type": type(e).__name__,
        }


def run_redshift_select(sql: str) -> str:
    logger.info("TOOL run_redshift_select foi chamada")

    if settings.DEV_OFFLINE:
        logger.info("DEV OFFLINE: mockando Redshift com dados realistas")
        result = _mock_sql_result(sql)

        return json.dumps(
            {
                "status": "success",
                "sql": sql,
                "result": result,
            },
            ensure_ascii=False,
        )

    result = _invoke_redshift_lambda({"sql": sql})

    return json.dumps(
        {
            "status": result.get("status", "success") if isinstance(result, dict) else "success",
            "sql": sql,
            "result": result,
        },
        ensure_ascii=False,
    )
