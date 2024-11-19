from typing import Any
from urllib.parse import urlparse

from pydantic import SecretStr, model_serializer


def secureUrl(url: str | None) -> str:
    if url is None:
        return ""

    parsed = urlparse(url)
    replaced = parsed._replace(netloc="{}:{}@{}".format("***", "***", parsed.hostname))
    return str(replaced.geturl())


class SecretUrl(SecretStr):
    pass


class SecretSerializeMixin:
    @model_serializer()
    def _serialize(self) -> dict[str, Any]:
        dump = self.__dict__
        for key, value in dump.items():
            if isinstance(value, SecretUrl):
                dump[key] = secureUrl(value.get_secret_value())
            elif isinstance(value, SecretStr):
                dump[key] = str(value)
        return dump
