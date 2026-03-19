import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User


async def _register_and_login(
    client: AsyncClient,
    db_session: AsyncSession,
    username: str,
    *,
    is_admin: bool = False,
) -> str:
    resp = await client.post(
        "/api/v1/auth/register",
        json={"username": username, "email": f"{username}@example.com", "password": "password123"},
    )
    assert resp.status_code == 201

    if is_admin:
        result = await db_session.execute(select(User).where(User.username == username))
        user = result.scalar_one()
        user.is_admin = True
        await db_session.commit()

    resp = await client.post(
        "/api/v1/auth/login",
        data={"username": username, "password": "password123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert resp.status_code == 200
    return resp.json()["access_token"]


async def _create_author_and_book(
    client: AsyncClient,
    headers: dict[str, str],
    *,
    author_name: str,
    book_title: str,
    genre: str = "Science Fiction",
) -> tuple[int, int]:
    resp = await client.post("/api/v1/authors/", json={"name": author_name}, headers=headers)
    assert resp.status_code == 201
    author_id = resp.json()["id"]

    resp = await client.post(
        "/api/v1/books/",
        json={"title": book_title, "main_genre": genre, "author_id": author_id},
        headers=headers,
    )
    assert resp.status_code == 201
    book_id = resp.json()["id"]
    return author_id, book_id


@pytest.mark.asyncio
async def test_error_responses_are_consistent(client: AsyncClient, db_session: AsyncSession):
    resp = await client.post(
        "/api/v1/auth/login",
        data={"username": "ghost", "password": "wrong-password"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert resp.status_code == 401
    assert resp.json()["error"]["code"] == "INVALID_CREDENTIALS"

    resp = await client.get("/api/v1/auth/me")
    assert resp.status_code == 401
    assert resp.json()["error"]["code"] == "AUTH_ERROR"

    resp = await client.post(
        "/api/v1/auth/register",
        json={"username": "ab", "email": "bad-email", "password": "123"},
    )
    assert resp.status_code == 422
    assert resp.json()["error"]["code"] == "VALIDATION_ERROR"

    user_token = await _register_and_login(client, db_session, "reader")
    resp = await client.post(
        "/api/v1/authors/",
        json={"name": "Forbidden Author"},
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert resp.status_code == 403
    assert resp.json()["error"]["code"] == "INSUFFICIENT_PERMISSIONS"


@pytest.mark.asyncio
async def test_reading_list_permissions_and_author_delete_behavior(
    client: AsyncClient, db_session: AsyncSession
):
    admin_token = await _register_and_login(client, db_session, "admin_case", is_admin=True)
    reader_token = await _register_and_login(client, db_session, "reader_case")
    outsider_token = await _register_and_login(client, db_session, "outsider_case")

    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    reader_headers = {"Authorization": f"Bearer {reader_token}"}
    outsider_headers = {"Authorization": f"Bearer {outsider_token}"}

    author_id, book_id = await _create_author_and_book(
        client,
        admin_headers,
        author_name="Delete Safe Author",
        book_title="Delete Safe Book",
        genre="Fantasy",
    )

    resp = await client.post("/api/v1/reading-list/", json={"book_id": book_id}, headers=reader_headers)
    assert resp.status_code == 201
    entry_id = resp.json()["id"]

    duplicate_resp = await client.post(
        "/api/v1/reading-list/",
        json={"book_id": book_id},
        headers=reader_headers,
    )
    assert duplicate_resp.status_code == 201
    assert duplicate_resp.json()["id"] == entry_id

    resp = await client.delete(f"/api/v1/reading-list/{entry_id}", headers=outsider_headers)
    assert resp.status_code == 403
    assert resp.json()["error"]["code"] == "READING_LIST_FORBIDDEN"

    resp = await client.delete(f"/api/v1/authors/{author_id}", headers=admin_headers)
    assert resp.status_code == 204

    resp = await client.get(f"/api/v1/books/{book_id}")
    assert resp.status_code == 200
    assert resp.json()["author_id"] is None

    resp = await client.delete(f"/api/v1/reading-list/{entry_id}", headers=reader_headers)
    assert resp.status_code == 204


@pytest.mark.asyncio
async def test_extended_analytics_endpoints(client: AsyncClient, db_session: AsyncSession):
    admin_token = await _register_and_login(client, db_session, "analytics_admin", is_admin=True)
    reviewer_token = await _register_and_login(client, db_session, "analytics_user")

    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    reviewer_headers = {"Authorization": f"Bearer {reviewer_token}"}

    resp = await client.post("/api/v1/authors/", json={"name": "Trend Author"}, headers=admin_headers)
    assert resp.status_code == 201
    author_id = resp.json()["id"]

    book_ids: list[int] = []
    for idx in range(10):
        resp = await client.post(
            "/api/v1/books/",
            json={
                "title": f"Trend Book {idx}",
                "main_genre": "Science Fiction",
                "author_id": author_id,
            },
            headers=admin_headers,
        )
        assert resp.status_code == 201
        book_ids.append(resp.json()["id"])

    for idx, book_id in enumerate(book_ids):
        resp = await client.post(
            "/api/v1/reviews/",
            json={"book_id": book_id, "rating": 5 if idx < 5 else 4, "review_text": "Strong book"},
            headers=reviewer_headers,
        )
        assert resp.status_code == 201

    resp = await client.get("/api/v1/analytics/genres/top-rated?min_ratings=1&limit=5")
    assert resp.status_code == 200
    genres = resp.json()
    assert genres
    assert genres[0]["genre"] == "Science Fiction"

    resp = await client.get("/api/v1/analytics/authors/trending?days=365&limit=5")
    assert resp.status_code == 200
    trending = resp.json()
    assert trending
    assert trending[0]["author_id"] == author_id


@pytest.mark.asyncio
async def test_book_validation_and_complete_rating_distribution(
    client: AsyncClient, db_session: AsyncSession
):
    admin_token = await _register_and_login(client, db_session, "books_admin", is_admin=True)
    user_token = await _register_and_login(client, db_session, "books_user")
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    user_headers = {"Authorization": f"Bearer {user_token}"}

    resp = await client.post(
        "/api/v1/books/",
        json={"title": "Broken Book", "author_id": 999999},
        headers=admin_headers,
    )
    assert resp.status_code == 404
    assert resp.json()["error"]["code"] == "AUTHOR_NOT_FOUND"

    author_id, book_id = await _create_author_and_book(
        client,
        admin_headers,
        author_name="Validation Author",
        book_title="Validation Book",
        genre="Science Fiction",
    )

    resp = await client.put(
        f"/api/v1/books/{book_id}",
        json={"isbn": "ISBN-123"},
        headers=admin_headers,
    )
    assert resp.status_code == 200

    _, other_book_id = await _create_author_and_book(
        client,
        admin_headers,
        author_name="Validation Author 2",
        book_title="Validation Book 2",
        genre="Science Fiction",
    )

    resp = await client.put(
        f"/api/v1/books/{other_book_id}",
        json={"isbn": "ISBN-123"},
        headers=admin_headers,
    )
    assert resp.status_code == 400
    assert resp.json()["error"]["code"] == "BOOK_ISBN_EXISTS"

    resp = await client.post(
        "/api/v1/reviews/",
        json={"book_id": book_id, "rating": 5, "review_text": "Great"},
        headers=user_headers,
    )
    assert resp.status_code == 201

    resp = await client.get(f"/api/v1/analytics/books/{book_id}/rating-distribution")
    assert resp.status_code == 200
    distribution = resp.json()["distribution"]
    assert distribution == {"1": 0, "2": 0, "3": 0, "4": 0, "5": 1}
