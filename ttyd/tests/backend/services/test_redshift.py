import boto3

_session: boto3.Session | None = None


def run_query(sql):
    return [{"col1": "val1"}]


def test_query_execution():
    result = run_query("SELECT 1")
    assert result is not None


def test_redshift_mock():
    # Exemplo simples (mock)
    result = {"status": "ok"}

    assert result["status"] == "ok"


### Antiga Classe redshift.py
"""
import boto3
import psycopg2
from psycopg2.extras import RealDictCursor
from backend.app_config.settings import settings

_session: boto3.Session | None = None

def get_aws_session() -> boto3.Session:
    global _session
    if _session is None:
        if settings.APP_ENV == "local":
            _session = boto3.Session(profile_name=settings.AWS_PROFILE)
        else:
            _session = boto3.Session()
    return _session


CLUSTER_ID = "record-id-dw-dev"
AWS_REGION = settings.AWS_REGION

REDSHIFT_HOST = settings.REDSHIFT_HOST
REDSHIFT_PORT = 5439
REDSHIFT_DB   = settings.REDSHIFT_DB
REDSHIFT_USER = settings.REDSHIFT_USER

QUERY = ""

SELECT
  url,
  SUM(qtd_acessos) AS total_acessos
FROM agg_tables.agg_evolucao_cadastral
GROUP BY url
ORDER BY total_acessos DESC
LIMIT 100;
""

def main():
    session = get_aws_session()

    redshift = session.client("redshift", region_name=AWS_REGION)

    print("Gerando credenciais temporárias via IAM...")
    creds = redshift.get_cluster_credentials(
        ClusterIdentifier=CLUSTER_ID,
        DbUser=REDSHIFT_USER,
        DbName=REDSHIFT_DB,
        DurationSeconds=900,
    )

    conn = None
    try:
        print("Conectando no Redshift...")
        conn = psycopg2.connect(
            host=REDSHIFT_HOST,
            port=REDSHIFT_PORT,
            dbname=REDSHIFT_DB,
            user=creds["DbUser"],
            password=creds["DbPassword"],
            sslmode="require",
        )
        conn.autocommit = True

        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(QUERY)
            rows = cur.fetchall()

        for r in rows:
            print(f"{r['url']} -> {r['total_acessos']}")

        print("✅ Conexão feita usando credenciais IAM temporárias (profile no local).")

    finally:
        if conn is not None:
            conn.close()

if __name__ == "__main__":
    main()



# tools/redshift.py

import re
import time
import logging
import boto3
from typing import Dict, Any, Optional, List
from strands import tool
from backend.app_config.settings import settings

logger = logging.getLogger(__name__)

FORBIDDEN = [
    r"\binsert\b", r"\bupdate\b", r"\bdelete\b", r"\bdrop\b",
    r"\balter\b", r"\bcreate\b", r"\btruncate\b",
    r"\bgrant\b", r"\brevoke\b", r"\bcopy\b", r"\bunload\b",
]


## Antiga Classe redshift.py

class RedshiftDataAPI:
    def __init__(
        self,
        region: str,
        database: str,
        workgroup: Optional[str] = None,
        cluster_identifier: Optional[str] = None,
        db_user: Optional[str] = None,
    ):
        self.client = boto3.client("redshift-data", region_name=region)
        self.database = database
        self.workgroup = workgroup
        self.db_user = db_user
        self.cluster_identifier = cluster_identifier

    def execute(self, sql: str, timeout: int = 60):
        resp = self.client.execute_statement(
            Database=self.database,
            Sql=sql,
            WorkgroupName=self.workgroup,
            cluster_identifier=self.cluster_identifier
        )
        stmt_id = resp["Id"]

        start = time.time()
        while True:
            desc = self.client.describe_statement(Id=stmt_id)
            if desc["Status"] in ("FINISHED", "FAILED", "ABORTED"):
                break
            if time.time() - start > timeout:
                raise TimeoutError("Timeout Redshift Data API")
            time.sleep(0.5)

        if desc["Status"] != "FINISHED":
            raise RuntimeError(desc.get("Error"))

        result = self.client.get_statement_result(Id=stmt_id)

        columns = [c["name"] for c in result["ColumnMetadata"]]
        rows = [
            [next(iter(col.values())) for col in record]
            for record in result["Records"]
        ]

        return {"columns": columns, "rows": rows}


_redshift = RedshiftDataAPI(
    region="us-east-1",
    database="dev",
    #workgroup="record-id-dw-dev",
    ClusterIdentifier=settings.CLUSTER_ID,
    db_user=settings.REDSHIFT_USER
)


def _validate_select(sql: str) -> str:
    s = sql.strip().lower()

    if not s.startswith("select"):
        raise ValueError("Apenas SELECT é permitido.")

    if ";" in s[:-1]:
        raise ValueError("Múltiplas instruções não permitidas.")

    for kw in FORBIDDEN:
        if re.search(kw, s):
            raise ValueError("Palavra-chave proibida detectada.")

    if "limit" not in s:
        sql = sql.rstrip() + " LIMIT 100"

    return sql


@tool
def redshift_schema() -> str:
    print("entrou na tool: redshift_schema")
    sql = ""
    SELECT table_schema, table_name, column_name, data_type, ordinal_position
    FROM information_schema.columns
    WHERE table_schema NOT IN ('pg_catalog', 'information_schema')
    ORDER BY table_schema, table_name, ordinal_position
    ""
    result = _redshift.execute(sql)

    from collections import defaultdict
    tables = defaultdict(list)

    for row in result["rows"]:
        schema, table, col, dtype, _ = row
        tables[(schema, table)].append(f"{col} {dtype}")

    lines = [
        f"- {schema}.{table}({', '.join(cols)})"
        for (schema, table), cols in tables.items()
    ]

    return "Esquema do banco:\n" + "\n".join(lines)


@tool
def run_redshift_select(sql: str) -> Dict[str, Any]:
    print("entrou na tool: run_redshift_select")
    try:
        sql = _validate_select(sql)
        return {"sql": sql, **_redshift.execute(sql)}
    except Exception as e:
        return {"error": str(e), "sql": sql}
"""
