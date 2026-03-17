import requests
from typing import Annotated
from app.logger import log_tool_call, log_tool_result


def http_get(
    url: Annotated[str, "URL to request"]
) -> str:

    log_tool_call("http_get", {"url": url})

    result = requests.get(url).text

    log_tool_result("http_get", result)

    return result