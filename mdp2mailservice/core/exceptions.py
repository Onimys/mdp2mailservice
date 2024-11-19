from typing import Union

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from pydantic_core import ErrorDetails
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_422_UNPROCESSABLE_ENTITY, HTTP_500_INTERNAL_SERVER_ERROR

EXCLUDE_VALIDATION_CONTENT = ["ctx", "input", "url"]


Loc = tuple[Union[int, str], ...]


class MultipleValidationErrors(Exception):
    def __init__(self, errors: list[ErrorDetails]):
        super().__init__()
        self.errors = errors


def create_exception_response(status_code: int, exc: Exception) -> JSONResponse:
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
            "error_type": type(exc).__name__,
            "errors": errors
            if isinstance(exc, (ValidationError, RequestValidationError, MultipleValidationErrors))
            else str(exc),
        },
        status_code=status_code,
    )


def register_exception(app: FastAPI):
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):  # type: ignore
        return create_exception_response(exc.status_code, exc)

    @app.exception_handler(RequestValidationError)
    async def http422_error_handler(request: Request, exc: RequestValidationError | ValidationError) -> JSONResponse:  # type: ignore
        return create_exception_response(HTTP_422_UNPROCESSABLE_ENTITY, exc)

    @app.exception_handler(ValueError)
    async def value_exception_handler(request: Request, exc: ValueError):  # type: ignore
        return create_exception_response(HTTP_400_BAD_REQUEST, exc)

    @app.exception_handler(Exception)
    async def all_exception_handler(request: Request, exc: Exception):  # type: ignore
        return create_exception_response(HTTP_500_INTERNAL_SERVER_ERROR, exc)

    @app.exception_handler(MultipleValidationErrors)
    async def multiple_exception_handler(_request, exc: MultipleValidationErrors):  # type: ignore
        return create_exception_response(HTTP_422_UNPROCESSABLE_ENTITY, exc)
