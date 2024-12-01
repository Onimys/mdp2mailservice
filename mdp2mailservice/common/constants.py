from dataclasses import dataclass


@dataclass(frozen=True)
class Environment:
    DEVELOPMENT: str = "development"
    PRODUCTION: str = "production"
