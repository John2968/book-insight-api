import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User


async def _register_and_login(client: AsyncClient, username: str) -> str:
    resp = await client.post(
        "/api/v1/auth/register",
        json={"username": username, "email": f"{username}@example.com", "password": "password123"},
    )
    assert resp.status_code == 201
    resp = await client.post(
        "/api/v1/auth/login",
        data={"username": username, "password": "password123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    return resp.json()["access_token"]


@pytest.mark.asyncio
async def test_reviews_and_analytics(
    client: AsyncClient, db_session: AsyncSession
):
    token = await _register_and_login(client, "alice")
    headers = {"Authorization": f"Bearer {token}"}

    result = await db_session.execute(select(User).where(User.username == "alice"))
    user = result.scalar_one()
    user.is_admin = True
    await db_session.commit()

    # 创建作者和书
    resp = await client.post(
        "/api/v1/authors/",
        json={"name": "Author X"},
        headers=headers,
    )
    assert resp.status_code == 201
    author_id = resp.json()["id"]

    resp = await client.post(
        "/api/v1/books/",
        json={"title": "Book X", "main_genre": "Sci-Fi", "author_id": author_id},
        headers=headers,
    )
    assert resp.status_code == 201
    book_id = resp.json()["id"]

    # 创建两条评论
    for rating in (5, 4):
        resp = await client.post(
            "/api/v1/reviews/",
            json={"book_id": book_id, "rating": rating, "review_text": "Nice"},
            headers=headers,
        )
        assert resp.status_code == 201

    # 检查评分分布
    resp = await client.get(f"/api/v1/analytics/books/{book_id}/rating-distribution")
    assert resp.status_code == 200
    dist = resp.json()["distribution"]
    assert dist.get("5") == 1
    assert dist.get("4") == 1

    # 检查推荐接口返回列表
    resp = await client.get("/api/v1/analytics/users/me/recommendations", headers=headers)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)

