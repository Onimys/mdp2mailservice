from typing import Union

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from pydantic_core import ErrorDetails
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_422_UNPROCESSABLE_ENTITY, HTTP_500_INTERNAL_SERVER_ERROR

Loc = tuple[Union[int, str], ...]


class BaseInternalException(Exception):
    """
    Base error class for inherit all internal errors.
    """

    _status_code = 0
    _message = ""

    def __init__(
        self,
        status_code: int | None = None,
        message: str | None = None,
        errors: list[str] | None = None,
    ) -> None:
        self.status_code = status_code
        self.message = message
        self.errors = errors

    def get_status_code(self) -> int:
        return self.status_code or self._status_code

    def get_message(self) -> str:
        return self.message or self._message

    def __str__(self) -> str:
        return self.get_message()

    @classmethod
    def get_response(cls) -> JSONResponse:
        return JSONResponse(
            {
                "status_code": cls._status_code,
                "type": cls.__name__,
                "errors": cls._message,
            },
            status_code=cls._status_code,
        )


class RateLimitExceededException(BaseInternalException):
    """Exception raised when rate limit exceeded during specific time."""

    _status_code = 429
    _message = "Rate limit exceeded. Please try again later."


class MaxFileSizeExceededException(BaseInternalException):
    """Exception raised when file size is too large."""

    _status_code = 400
    _message = "File size too large."


class IncorrectFileExtensionException(BaseInternalException):
    """Exception raised when incorrect file extension."""

    _status_code = 400
    _message = "Incorrect file extension."


class MultipleValidationErrors(Exception):
    def __init__(self, errors: list[ErrorDetails]):
        super().__init__()
        self.errors = errors


def create_exception_response(status_code: int, exc: Exception) -> JSONResponse:
    EXCLUDE_VALIDATION_CONTENT = ["ctx", "input", "url"]
    errors = None
    if isinstance(exc, (ValidationError, RequestValidationError, MultipleValidationErrors)):
        if isinstance(exc, (MultipleValidationErrors)):
            errors = exc.errors
        else:
            errors = exc.errors()

        for error in errors:
            for key in EXCLUDE_VALIDATION_CONTENT:
                if key in error:
                    del error[key]

    return JSONResponse(
        {
            "status_code": status_code,
            "type": type(exc).__name__,
            "errors": errors
            if isinstance(exc, (ValidationError, RequestValidationError, MultipleValidationErrors))
            else str(exc),
        },
        status_code=status_code,
    )


def register_exceptions(app: FastAPI):
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):  # type: ignore
        return create_exception_response(exc.status_code, exc)

    @app.exception_handler(BaseInternalException)
    async def internal_exception_handler(_: Request, exc: BaseInternalException) -> JSONResponse:  # type: ignore
        return create_exception_response(exc.get_status_code(), exc)

    @app.exception_handler(ValueError)
    async def value_exception_handler(request: Request, exc: ValueError):  # type: ignore
        return create_exception_response(HTTP_400_BAD_REQUEST, exc)

    @app.exception_handler(RequestValidationError)
    async def http422_error_handler(request: Request, exc: RequestValidationError | ValidationError) -> JSONResponse:  # type: ignore
        return create_exception_response(HTTP_422_UNPROCESSABLE_ENTITY, exc)

    @app.exception_handler(MultipleValidationErrors)
    async def multiple_exception_handler(_request, exc: MultipleValidationErrors):  # type: ignore
        return create_exception_response(HTTP_422_UNPROCESSABLE_ENTITY, exc)

    @app.exception_handler(Exception)
    async def all_exception_handler(request: Request, exc: Exception):  # type: ignore
        return create_exception_response(HTTP_500_INTERNAL_SERVER_ERROR, exc)
