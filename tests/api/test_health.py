from httpx import AsyncClient


async def test_health(client: AsyncClient):
    response = await client.get("http://test/health/status")
    assert response.status_code == 200
    assert response.json()["status"] == "Ok"
