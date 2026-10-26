"""Uniform translation of application and framework exceptions."""

import logging
from typing import Any

from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException

from arsis.core.errors import DomainError
from arsis.core.request_context import REQUEST_ID_HEADER

logger = logging.getLogger(__name__)


def _request_id(request: Request) -> str:
    return str(getattr(request.state, "request_id", "unknown"))


def _response(
    request: Request,
    *,
    status_code: int,
    code: str,
    message: str,
    details: Any | None = None,
    headers: dict[str, str] | None = None,
) -> JSONResponse:
    response_headers = dict(headers or {})
    response_headers[REQUEST_ID_HEADER] = _request_id(request)
    return JSONResponse(
        status_code=status_code,
        headers=response_headers,
        content=jsonable_encoder(
            {
                "error": {
                    "code": code,
                    "message": message,
                    "details": details,
                    "request_id": _request_id(request),
                }
            }
        ),
    )


async def domain_error_handler(request: Request, exception: Exception) -> JSONResponse:
    if not isinstance(exception, DomainError):  # pragma: no cover - registration guarantees it
        raise exception
    return _response(
        request,
        status_code=exception.status_code,
        code=exception.code,
        message=exception.message,
        details=exception.details,
        headers=exception.headers,
    )


async def validation_error_handler(request: Request, exception: Exception) -> JSONResponse:
    if not isinstance(exception, RequestValidationError):  # pragma: no cover
        raise exception
    return _response(
        request,
        status_code=422,
        code="VALIDATION_ERROR",
        message="La richiesta contiene dati non validi",
        details={"issues": exception.errors()},
    )


async def http_error_handler(request: Request, exception: Exception) -> JSONResponse:
    if not isinstance(exception, HTTPException):  # pragma: no cover
        raise exception
    detail = exception.detail
    if isinstance(detail, dict):
        code = str(detail.get("code", "HTTP_ERROR"))
        message = str(detail.get("message", "Richiesta non completata"))
        details = detail.get("details")
    else:
        code = "HTTP_ERROR"
        message = str(detail)
        details = None
    return _response(
        request,
        status_code=exception.status_code,
        code=code,
        message=message,
        details=details,
        headers=dict(exception.headers or {}),
    )


async def unexpected_error_handler(request: Request, exception: Exception) -> JSONResponse:
    logger.exception("Unhandled request error", exc_info=exception)
    return _response(
        request,
        status_code=500,
        code="INTERNAL_SERVER_ERROR",
        message="Errore interno del server",
    )


def install_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(DomainError, domain_error_handler)
    app.add_exception_handler(RequestValidationError, validation_error_handler)
    app.add_exception_handler(HTTPException, http_error_handler)
    app.add_exception_handler(Exception, unexpected_error_handler)
