from dataclasses import dataclass


@dataclass(frozen=True)
class Environment:
    DEVELOPMENT: str = "dev"
    PRODUCTION: str = "prod"
