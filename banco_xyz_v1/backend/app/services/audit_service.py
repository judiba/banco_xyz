from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")



def append_audit(state: dict[str, Any], step: str, **kwargs: Any) -> dict[str, Any]:
    audit_log = state.get("audit_log", [])
    audit_log.append({"step": step, "at": utc_now_iso(), **kwargs})
    state["audit_log"] = audit_log
    return state
