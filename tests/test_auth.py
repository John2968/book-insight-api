import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_and_login_and_me(client: AsyncClient):
    resp = await client.post(
        "/api/v1/auth/register",
        json={"username": "bob", "email": "bob@example.com", "password": "password123"},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["username"] == "bob"
    assert data["is_active"] is True

    resp = await client.post(
        "/api/v1/auth/login",
        data={"username": "bob", "password": "password123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert resp.status_code == 200
    token = resp.json()["access_token"]
    assert token

    resp = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    me = resp.json()
    assert me["username"] == "bob"

