from __future__ import annotations

from uuid import uuid4

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from backend.api.v1.schemas.common import ErrorBody, ErrorDetail, ErrorEnvelope


class ApiException(Exception):
    def __init__(
        self,
        status_code: int,
        code: str,
        message: str,
        details: list[ErrorDetail] | None = None,
    ):
        self.status_code = status_code
        self.code = code
        self.message = message
        self.details = details or []


def _request_id(request: Request) -> str:
    return request.headers.get("X-Request-Id") or str(uuid4())


def error_response(
    request: Request,
    status_code: int,
    code: str,
    message: str,
    details: list[ErrorDetail] | None = None,
) -> JSONResponse:
    body = ErrorEnvelope(
        error=ErrorBody(
            code=code,
            message=message,
            details=details or [],
            requestId=_request_id(request),
        )
    )
    return JSONResponse(status_code=status_code, content=body.model_dump())


async def api_exception_handler(request: Request, exc: ApiException) -> JSONResponse:
    return error_response(
        request,
        exc.status_code,
        exc.code,
        exc.message,
        exc.details,
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    code = "INTERNAL_ERROR"
    if exc.status_code == 404:
        code = "NOT_FOUND"
    elif exc.status_code == 401:
        code = "AUTH_TOKEN_EXPIRED"
    return error_response(request, exc.status_code, code, str(exc.detail))


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    details = [
        ErrorDetail(
            field=".".join(str(p) for p in err.get("loc", []) if p != "body"),
            message=err.get("msg", "Valor inválido"),
        )
        for err in exc.errors()
    ]
    return error_response(
        request,
        422,
        "VALIDATION_ERROR",
        "Dados inválidos.",
        details,
    )
