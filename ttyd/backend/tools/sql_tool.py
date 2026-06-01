from backend.tools.registry import register_tool


@register_tool("run_sql")
def run_sql(query): ...
