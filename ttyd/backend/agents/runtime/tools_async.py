# backend/agents/runtime/tools_async.py
# This module contains asynchronous implementations of tools that can be used by agents.


async def execute_tool(tool, ctx):
    """Execute a tool asynchronously.

    Args:
        tool: The tool to execute
        ctx: The agent context

    Returns:
        The result of the tool execution
    """
    result = await tool.run(ctx)

    return result
