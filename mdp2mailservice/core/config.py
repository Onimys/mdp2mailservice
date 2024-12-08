import os
import tomllib
from functools import lru_cache
from pathlib import Path
from typing import Final, Sequence

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

from mdp2mailservice.common.utils.security import SecretSerializeMixin, SecretUrl

from ..common.constants import Environment

APP_FOLDER: Final = Path(__file__).parent.parent.parent
TEMPLATE_FOLDER: Final = "templates"


def get_app_version() -> str:
    with open("pyproject.toml", "rb") as f:
        pyproject = tomllib.load(f)
    varsion: str = pyproject["tool"]["poetry"]["version"]

    return varsion


def get_app_name() -> str:
    with open("pyproject.toml", "rb") as f:
        pyproject = tomllib.load(f)
    name: str = pyproject["tool"]["poetry"]["name"]

    return name


class Config(SecretSerializeMixin, BaseSettings):
    ENVIRONMENT: str = Environment.PRODUCTION
    API_PREFIX: str = "/api/v1"
    ROOT_PATH: str = ""

    DATABASE_URL: SecretUrl

    LOG_LEVEL: str = "INFO"
    LOGS_FOLDER: str = "logs"

    SMTP_HOST: str
    SMTP_PORT: int = 25
    SMTP_USERNAME: str
    SMTP_PASSWORD: SecretStr
    SMTP_FROM: str | None = None
    SMTP_USE_TLS: bool = False

    MAIL_QUEUE_CONSUMER_ENABLED: bool = False
    MAIL_QUEUE_CONSUMER_URL: SecretUrl | None = None
    MAIL_QUEUE_CONSUMER_QUEUE: str = "mdp2mailservice:send-mail"
    MAIL_QUEUE_CONSUMER_AUTO_DELETE: bool = False
    MAIL_QUEUE_CONSUMER_MAX_WORKERS: int = 10

    ALLOWED_HOSTS: list[str] = [
        "http://localhost",
        "http://localhost:8080",
        "http://127.0.0.1",
        "http://127.0.0.1:8080",
    ]
    ALLOWED_HOSTS_REGEX: str | None = None
    APP_NAME: str = get_app_name()
    APP_VERSION: str = get_app_version()

    ATTACHMENTS_FOLDER: str = f"{APP_FOLDER}/attachments/"
    ATTACHMENTS_TOTAL_SIZE: int = 25 * 1024 * 1024

    ADMIN_ENABLED: bool = True

    TEMPLATE_DEFAULT_TYPE: str = "jinja"
    TEMPLATE_FOLDER_PATH: str = f"{get_app_name()}/{TEMPLATE_FOLDER}"
    TEMPLATE_UPLOAD_MAX_SIZE: int = 5 * 1024 * 1024
    TEMPLATE_ALLOWED_EXTENSIONS: Sequence[str] = ("html", "jinja", "mjml")

    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_DURATION: int = 60
    RATE_LIMIT_REQUESTS: int = 1000

    model_config = SettingsConfigDict(env_file=f"{APP_FOLDER}/.env")


class TestConfig(Config):
    ENVIRONMENT: str = Environment.TEST
    model_config = SettingsConfigDict(env_file=f"{APP_FOLDER}/.env.test")


class DevConfig(Config):
    ENVIRONMENT: str = Environment.DEVELOPMENT
    model_config = SettingsConfigDict(env_file=(f"{APP_FOLDER}/.env", f"{APP_FOLDER}/.env.dev"))


environments: dict[str, type[Config]] = {
    Environment.DEVELOPMENT: DevConfig,
    Environment.TEST: TestConfig,
    Environment.PRODUCTION: Config,
}


@lru_cache
def get_app_settings() -> Config:
    """
    Return application config.
    """
    app_env = os.getenv("ENVIRONMENT", "production")
    config = environments[str(app_env)]
    return config()  # type: ignore


settings = get_app_settings()
