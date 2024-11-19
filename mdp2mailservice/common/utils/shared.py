from typing import Type

from fastapi import Form
from pydantic import BaseModel, ValidationError

from mdp2mailservice.core.exceptions import MultipleValidationErrors


def validate_multupart_json(model: Type[BaseModel]):
    def wrapper(body: str = Form(...)):
        try:
            return model.model_validate_json(body)
        except ValidationError as exc:
            errors = exc.errors()
            for error in errors:
                error["loc"] = tuple(["body"] + list(error["loc"]))
            raise MultipleValidationErrors(errors)

    return wrapper
