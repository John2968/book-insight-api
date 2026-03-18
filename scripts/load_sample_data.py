import asyncio
from datetime import datetime
from pathlib import Path
import sys

from sqlalchemy import func, select

# Allow running this script directly: `python scripts/load_sample_data.py`
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.core.security import get_password_hash
from app.db.session import AsyncSessionLocal
from app.models import Author, Book, Review, User


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
        created_at=datetime.utcnow(),
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    print(f"Created user: {username} (admin={is_admin})")
    return user


async def create_author(session, name: str, country: str | None = None) -> Author:
    result = await session.execute(select(Author).where(Author.name == name))
    author = result.scalar_one_or_none()
    if author:
        return author

    author = Author(name=name, country=country)
    session.add(author)
    await session.commit()
    await session.refresh(author)
    print(f"Created author: {name}")
    return author


async def create_book(
    session,
    title: str,
    author: Author,
    main_genre: str | None = None,
    isbn: str | None = None,
    description: str | None = None,
) -> Book:
    result = await session.execute(select(Book).where(Book.title == title))
    book = result.scalar_one_or_none()
    if book:
        return book

    book = Book(
        title=title,
        author_id=author.id,
        main_genre=main_genre,
        isbn=isbn,
        description=description,
        publication_date=None,
        cover_image_url=None,
        ratings_count=0,
        average_rating=None,
    )
    session.add(book)
    await session.commit()
    await session.refresh(book)
    print(f"Created book: {title}")
    return book


async def add_review(session, user: User, book: Book, rating: int, text: str | None = None) -> None:
    review = Review(
        user_id=user.id,
        book_id=book.id,
        rating=rating,
        review_text=text,
        created_at=datetime.utcnow(),
    )
    session.add(review)
    await session.commit()

    # update book stats
    stats_query = select(func.count(Review.id), func.avg(Review.rating)).where(Review.book_id == book.id)
    stats_result = await session.execute(stats_query)
    count, avg = stats_result.one()
    book.ratings_count = int(count or 0)
    book.average_rating = float(avg) if avg is not None else None
    await session.commit()


async def main() -> None:
    async with AsyncSessionLocal() as session:
        # users
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

        # authors
        a1 = await create_author(session, "Isaac Asimov", "USA")
        a2 = await create_author(session, "J. K. Rowling", "UK")
        a3 = await create_author(session, "Haruki Murakami", "Japan")

        # books
        b1 = await create_book(
            session,
            title="Foundation",
            author=a1,
            main_genre="Science Fiction",
            description="A science fiction classic about the fall of the Galactic Empire.",
        )
        b2 = await create_book(
            session,
            title="Harry Potter and the Philosopher's Stone",
            author=a2,
            main_genre="Fantasy",
            description="The first book in the Harry Potter series.",
        )
        b3 = await create_book(
            session,
            title="Norwegian Wood",
            author=a3,
            main_genre="Literary Fiction",
            description="A nostalgic story of loss and sexuality.",
        )

        # reviews
        await add_review(session, user, b1, 5, "Amazing sci-fi worldbuilding.")
        await add_review(session, user, b1, 4, "Great ideas, a bit dated in style.")
        await add_review(session, user, b2, 5, "Loved it as a kid.")
        await add_review(session, user, b2, 4, "Still enjoyable on reread.")
        await add_review(session, user, b3, 3, "Beautiful writing but slow pace.")

    print("Sample data loaded successfully.")


if __name__ == "__main__":
    asyncio.run(main())

