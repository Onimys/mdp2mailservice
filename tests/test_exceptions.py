import json
from typing import Any

import pytest
from fastapi import HTTPException
from fastapi.exceptions import RequestValidationError

from mdp2mailservice.core.exceptions import create_exception_response


@pytest.mark.parametrize(
    "status_code,exception,expected_error_type",
    [
        (500, Exception(), str),
        (404, HTTPException(status_code=404), str),
        (400, HTTPException(status_code=400), str),
    ],
)
def test_exception_response(status_code: int, exception: Exception, expected_error_type: Any):
    response = create_exception_response(status_code, exception)

    assert isinstance(response.body, bytes)
    content = json.loads(response.body)

    assert response.status_code == status_code
    assert content["error_type"] == type(exception).__name__
    assert isinstance(content["errors"], expected_error_type)


def test_validation_exception_response():
    response = create_exception_response(422, RequestValidationError(errors=[]))

    assert isinstance(response.body, bytes)
    content = json.loads(response.body)

    assert response.status_code == 422
    assert content["error_type"] == RequestValidationError.__name__

    assert isinstance(content["errors"], list)
    assert len(content["errors"]) == 0
