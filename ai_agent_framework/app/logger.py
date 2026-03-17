import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger("agent_logger")


def log_tool_call(name: str, args: dict):
    logger.info(f"Tool called: {name} | args={args}")


def log_tool_result(name: str, result: str):
    logger.info(f"Tool result: {name} | size={len(str(result))}")