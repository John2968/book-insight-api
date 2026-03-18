import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User


async def _create_admin_and_get_token(
    client: AsyncClient, db_session: AsyncSession
) -> str:
    resp = await client.post(
        "/api/v1/auth/register",
        json={"username": "admin", "email": "admin@example.com", "password": "admin123"},
    )
    assert resp.status_code == 201

    result = await db_session.execute(select(User).where(User.username == "admin"))
    user = result.scalar_one()
    user.is_admin = True
    await db_session.commit()

    resp = await client.post(
        "/api/v1/auth/login",
        data={"username": "admin", "password": "admin123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    return resp.json()["access_token"]


@pytest.mark.asyncio
async def test_author_and_book_crud_flow(client: AsyncClient, db_session: AsyncSession):
    token = await _create_admin_and_get_token(client, db_session)
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

