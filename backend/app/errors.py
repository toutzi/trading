from enum import Enum

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


class ErrorCode(str, Enum):
    INVALID_CREDENTIALS = "invalid_credentials"
    UNAUTHORIZED = "unauthorized"
    INVALID_TOKEN = "invalid_token"
    VALIDATION_ERROR = "validation_error"
    NOT_FOUND = "not_found"
    INTERNAL_ERROR = "internal_error"


class ApiError(Exception):
    def __init__(self, code: ErrorCode, message: str, status_code: int = 400):
        self.code = code.value if isinstance(code, ErrorCode) else code
        self.message = message
        self.status_code = status_code


def error_response(code: str, message: str, status_code: int) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"error": {"code": code, "message": message}},
    )


def _format_validation_errors(exc: RequestValidationError) -> str:
    parts = []
    for err in exc.errors()[:5]:
        loc = ".".join(str(x) for x in err.get("loc", []) if x != "body")
        msg = err.get("msg", "invalid value")
        parts.append(f"{loc}: {msg}" if loc else msg)
    return "Invalid request: " + "; ".join(parts)


_STATUS_TO_CODE = {
    401: ErrorCode.UNAUTHORIZED.value,
    403: ErrorCode.UNAUTHORIZED.value,
    404: ErrorCode.NOT_FOUND.value,
    422: ErrorCode.VALIDATION_ERROR.value,
}


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(ApiError)
    async def _api_error(request: Request, exc: ApiError):
        return error_response(exc.code, exc.message, exc.status_code)

    @app.exception_handler(RequestValidationError)
    async def _validation_error(request: Request, exc: RequestValidationError):
        return error_response(
            ErrorCode.VALIDATION_ERROR.value,
            _format_validation_errors(exc),
            422,
        )

    @app.exception_handler(StarletteHTTPException)
    async def _http_error(request: Request, exc: StarletteHTTPException):
        code = _STATUS_TO_CODE.get(exc.status_code, ErrorCode.INTERNAL_ERROR.value)
        message = str(exc.detail) if exc.detail else "Request failed"
        return error_response(code, message, exc.status_code)

    @app.exception_handler(Exception)
    async def _unhandled_error(request: Request, exc: Exception):
        return error_response(ErrorCode.INTERNAL_ERROR.value, "Internal server error", 500)
