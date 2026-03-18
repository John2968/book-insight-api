import pytest
from httpx import AsyncClient


async def _create_admin_and_get_token(client: AsyncClient) -> str:
    resp = await client.post(
        "/api/v1/auth/register",
        json={"username": "admin", "email": "admin@example.com", "password": "admin123"},
    )
    assert resp.status_code == 201

    # 手动将用户设为管理员
    from app.models import User
    from app.db.session import AsyncSessionLocal
    from sqlalchemy import select

    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.username == "admin"))
        user = result.scalar_one()
        user.is_admin = True
        await session.commit()

    resp = await client.post(
        "/api/v1/auth/login",
        data={"username": "admin", "password": "admin123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    return resp.json()["access_token"]


@pytest.mark.asyncio
async def test_author_and_book_crud_flow(client: AsyncClient):
    token = await _create_admin_and_get_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    resp = await client.post(
        "/api/v1/authors/",
        json={"name": "Test Author", "country": "UK"},
        headers=headers,
    )
    assert resp.status_code == 201
    author_id = resp.json()["id"]

    resp = await client.post(
        "/api/v1/books/",
        json={"title": "Test Book", "main_genre": "Test Genre", "author_id": author_id},
        headers=headers,
    )
    assert resp.status_code == 201
    book_id = resp.json()["id"]

    resp = await client.get("/api/v1/books/?search=Test")
    assert resp.status_code == 200
    books = resp.json()
    assert any(b["id"] == book_id for b in books)

    resp = await client.put(
        f"/api/v1/books/{book_id}",
        json={"description": "Updated description"},
        headers=headers,
    )
    assert resp.status_code == 200
    assert resp.json()["description"] == "Updated description"

    resp = await client.delete(f"/api/v1/books/{book_id}", headers=headers)
    assert resp.status_code == 204

