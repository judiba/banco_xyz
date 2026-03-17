import requests
from typing import Annotated
from app.logger import log_tool_call, log_tool_result


def bible_lookup(
    route: Annotated[str, "Example: /john+3:16"]
) -> str:

    log_tool_call("bible_lookup", {"route": route})

    url = f"https://bible-api.com{route}"

    response = requests.get(url).text

    log_tool_result("bible_lookup", response)

    return response