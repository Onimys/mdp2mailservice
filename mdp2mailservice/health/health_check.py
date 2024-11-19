from typing import Literal

from fastapi import APIRouter, Request
from pydantic import BaseModel

from mdp2mailservice.core.config import Config, settings

router = APIRouter()


class Health(BaseModel):
    status: Literal["Ok"]
    config: Config | None = None


@router.get("/status", name="check", description="Check health of service", response_model_exclude_none=True)
def read_root(request: Request) -> Health:
    assert request.client

    client_host = request.client.host
    if client_host == "127.0.0.1":
        return Health(status="Ok", config=settings)

    return Health(status="Ok")
