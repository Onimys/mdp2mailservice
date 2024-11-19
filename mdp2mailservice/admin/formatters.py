from typing import Any, Type

from sqlalchemy import Column

from mdp2mailservice.common.bases.models import TModel


def truncate_value(attr: str, max_length: int) -> Any:
    def wrapper(value: Type[TModel], _: Column[TModel]) -> Any:
        return f"{value.__dict__[attr][:max_length - 3]}..."

    return wrapper
