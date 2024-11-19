from typing import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient

from mdp2mailservice.core.config import settings
from mdp2mailservice.main import app


@pytest.fixture(scope="session")
async def client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        client.base_url = client.base_url.join(settings.API_PREFIX)
        yield client
