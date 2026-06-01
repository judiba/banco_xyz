# backend/agents/runtime/tools_async.py


async def execute_tool(tool, ctx):
    result = await tool.run(ctx)

    return result
