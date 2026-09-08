"""Application-level exception hierarchy and FastAPI exception handlers."""

from __future__ import annotations

from typing import Any, Dict, Optional

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.logging import get_logger

logger = get_logger(__name__)


def _error_response(
    code: str,
    message: str,
    details: Optional[Dict[str, Any]] = None,
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
) -> JSONResponse:
    body: Dict[str, Any] = {"error": {"code": code, "message": message}}
    if details:
        body["error"]["details"] = details
    return JSONResponse(content=body, status_code=status_code)


class IPSaktiError(Exception):
    """Base exception for all domain errors."""

    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    code: str = "INTERNAL_ERROR"

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}


class NotFoundError(IPSaktiError):
    status_code = status.HTTP_404_NOT_FOUND
    code = "NOT_FOUND"


class AuthenticationError(IPSaktiError):
    status_code = status.HTTP_401_UNAUTHORIZED
    code = "AUTHENTICATION_FAILED"


class AuthorizationError(IPSaktiError):
    status_code = status.HTTP_403_FORBIDDEN
    code = "FORBIDDEN"


class ValidationError(IPSaktiError):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    code = "VALIDATION_ERROR"


class RateLimitError(IPSaktiError):
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    code = "RATE_LIMIT_EXCEEDED"


class RAGError(IPSaktiError):
    """Raised when the RAG pipeline fails unrecoverably."""
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    code = "RAG_ERROR"


class InsufficientEvidenceError(IPSaktiError):
    """Raised when the system must abstain due to insufficient evidence."""
    status_code = status.HTTP_200_OK
    code = "INSUFFICIENT_EVIDENCE"


def register_exception_handlers(app: FastAPI) -> None:
    """Attach all custom exception handlers to the FastAPI app."""

    @app.exception_handler(IPSaktiError)
    async def domain_exception_handler(
        request: Request, exc: IPSaktiError
    ) -> JSONResponse:
        logger.warning(
            "domain_exception",
            code=exc.code,
            message=exc.message,
            path=str(request.url),
        )
        return _error_response(
            code=exc.code,
            message=exc.message,
            details=exc.details or None,
            status_code=exc.status_code,
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        logger.info(
            "validation_error",
            errors=exc.errors(),
            path=str(request.url),
        )
        return _error_response(
            code="VALIDATION_ERROR",
            message="Request validation failed.",
            details={"errors": exc.errors()},
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        logger.error(
            "unhandled_exception",
            exc_info=exc,
            path=str(request.url),
        )
        return _error_response(
            code="INTERNAL_ERROR",
            message="An unexpected internal error occurred.",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
