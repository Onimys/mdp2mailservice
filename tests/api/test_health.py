from httpx import AsyncClient


async def test_health(test_client: AsyncClient):
    response = await test_client.get("http://test/health-check")
    assert response.status_code == 200
    assert response.json()["status"] == "Ok"
