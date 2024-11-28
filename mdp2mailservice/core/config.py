import tomllib
from pathlib import Path

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

from mdp2mailservice.common.utils.security import SecretSerializeMixin, SecretUrl

from ..common.constants import Environment

app_folder = Path(__file__).parent.parent.parent


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

    ATTACHMENTS_FOLDER: str = f"{app_folder}/attachments/"
    ATTACHMENTS_TOTAL_SIZE: int = 10 * 1024 * 1024

    ADMIN_ENABLED: bool = True

    TEMPLATE_DEFAULT_TYPE: str = "jinja"
    TEMPLATE_FOLDER: str = f"{get_app_name()}/templates"

    model_config = SettingsConfigDict(env_file=f"{app_folder}/.env")


settings = Config()  # type: ignore
