BASE_RULES = """
- Apenas SELECT
- Não usar SELECT *
- Não usar outras tabelas
- Usar apenas colunas permitidas
- Use GROUP BY 1 quando houver agregação
- Use ORDER BY 1
- Nunca use alias no ORDER BY

Regras obrigatórias adicionais:
- Use sintaxe compatível com Amazon Redshift
- Para subtração de datas use INTERVAL (ex: data - INTERVAL '1 month')
- Nunca use DATEADD sem aspas no parâmetro de unidade
- Nunca use DATE_SUB
- Nunca use DATE_ADD
- Para subtração de datas use:
    data - INTERVAL 'X days'
- Ou use DATEADD(day, -X, data)
- Nunca use sintaxe MySQL ou BigQuery

REGRAS DE PERÍODO (OBRIGATÓRIO):
- Quando a pergunta mencionar qualquer período relativo (ex: "últimas X semanas", "últimos X dias"),
  é PROIBIDO usar CURRENT_DATE, GETDATE(), NOW() ou SYSDATE.
- O período deve SEMPRE ser calculado com base na maior data disponível na tabela.
- Nunca use datas fixas quando o usuário pedir período relativo.

FORMATO DE SAÍDA (OBRIGATÓRIO)
- Não use markdown ou blocos de código.
- Não inclua explicações ou texto adicional.
- Sempre que houver divisão, proteger o denominador com NULLIF(denominador, 0)
"""


def build_text_to_sql_prompt(pergunta: str, tabela_completa: str, schema_filtrado: str) -> str:
    return f"""
  Use as seguintes informações para a construção da query do Redshift:
    Tabela permitida:
    {tabela_completa}

    Colunas permitidas:
    {schema_filtrado}

    Pergunta:
    {pergunta}

    Regras obrigatórias:
    {BASE_RULES}

  Retorne somente a SQL.
  """
