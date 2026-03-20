import asyncio
from datetime import datetime, timezone
from pathlib import Path
import sys

from sqlalchemy import func, select

# Allow running this script directly: `python scripts/seed_demo_users_and_reviews.py`
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.core.security import get_password_hash
from app.db.session import AsyncSessionLocal
from app.models import Book, Review, User
from scripts.import_books_from_csv import DEFAULT_CSV, import_books_from_csv


async def create_user(session, username: str, email: str, password: str, is_admin: bool = False) -> User:
    result = await session.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    if user:
        return user

    user = User(
        username=username,
        email=email,
        password_hash=get_password_hash(password),
        is_active=True,
        is_admin=is_admin,
        created_at=datetime.now(timezone.utc),
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    print(f"Created user: {username} (admin={is_admin})")
    return user


async def get_book_by_title(session, title: str) -> Book:
    result = await session.execute(select(Book).where(Book.title == title))
    book = result.scalar_one_or_none()
    if book is None:
        raise RuntimeError(f"Expected imported public book not found: {title}")
    return book


async def add_review(session, user: User, book: Book, rating: int, text: str | None = None) -> None:
    existing_result = await session.execute(
        select(Review).where(
            Review.user_id == user.id,
            Review.book_id == book.id,
            Review.rating == rating,
            Review.review_text == text,
        )
    )
    if existing_result.scalar_one_or_none():
        return

    review = Review(
        user_id=user.id,
        book_id=book.id,
        rating=rating,
        review_text=text,
        created_at=datetime.now(timezone.utc),
    )
    session.add(review)
    await session.commit()

    # Update book stats after inserting the demo review.
    stats_query = select(func.count(Review.id), func.avg(Review.rating)).where(Review.book_id == book.id)
    stats_result = await session.execute(stats_query)
    count, avg = stats_result.one()
    book.ratings_count = int(count or 0)
    book.average_rating = float(avg) if avg is not None else None
    await session.commit()


async def main() -> None:
    async with AsyncSessionLocal() as session:
        imported_books = await import_books_from_csv(session, DEFAULT_CSV)
        if imported_books:
            print(f"Imported {imported_books} public Open Library books before seeding demo users/reviews.")

        # Demo users for auth/admin flows.
        await create_user(
            session,
            username="admin",
            email="admin@example.com",
            password="admin123",
            is_admin=True,
        )
        user = await create_user(
            session,
            username="alice",
            email="alice@example.com",
            password="password123",
            is_admin=False,
        )

        # Attach demo reviews to real imported public books.
        b1 = await get_book_by_title(session, "The Martian")
        b2 = await get_book_by_title(session, "Kindred")
        b3 = await get_book_by_title(session, "Jane Eyre")

        await add_review(session, user, b1, 5, "Fast-paced and accessible science fiction on a real imported title.")
        await add_review(session, user, b1, 4, "Strong problem-solving theme and clear pacing.")
        await add_review(session, user, b2, 5, "A powerful book for demonstrating reviews on imported metadata.")
        await add_review(session, user, b2, 4, "Interesting themes and a memorable premise.")
        await add_review(session, user, b3, 4, "Classic novel with strong character writing.")

    print("Demo users and reviews loaded successfully on top of the imported Open Library dataset.")


if __name__ == "__main__":
    asyncio.run(main())
