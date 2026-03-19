"""
Import books (and authors) from a CSV file into the database.

Supports Goodreads-style columns: title, authors, average_rating, isbn,
ratings_count, publication_date, genre (or main_genre). Column names are
case-insensitive and flexible (e.g. "Authors" or "authors").

Usage:
  python scripts/import_books_from_csv.py                          # uses data/raw/open_library_books.csv
  python scripts/import_books_from_csv.py data/raw/open_library_books.csv
  python scripts/import_books_from_csv.py data/raw/books.csv       # use your own CSV
"""
import asyncio
import csv
import re
import sys
from datetime import date
from pathlib import Path

# Allow running this script directly
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import AsyncSessionLocal
from app.models import Author, Book


DEFAULT_CSV = REPO_ROOT / "data" / "raw" / "open_library_books.csv"


def _normalize_headers(row: dict) -> dict:
    """Lowercase keys and strip whitespace for flexible column names."""
    return {k.strip().lower(): v for k, v in row.items() if k and k.strip()}


def _column(row: dict, *candidates: str, default: str = "") -> str:
    for c in candidates:
        if c in row and row[c] is not None:
            val = str(row[c]).strip()
            if val:
                return val
    return default


def _parse_date(val: str) -> date | None:
    if not val or not str(val).strip():
        return None
    val = str(val).strip()
    # Year only
    if re.match(r"^\d{4}$", val):
        return date(int(val), 1, 1)
    # YYYY-MM-DD or similar
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y"):
        try:
            from datetime import datetime
            return datetime.strptime(val[:10], fmt).date()
        except ValueError:
            continue
    return None


def _float(val: str) -> float | None:
    if val is None or str(val).strip() == "":
        return None
    try:
        return float(str(val).replace(",", "."))
    except ValueError:
        return None


def _int(val: str) -> int:
    if val is None or str(val).strip() == "":
        return 0
    try:
        return int(float(str(val).replace(",", ".")))
    except ValueError:
        return 0


async def get_or_create_author(session: AsyncSession, name: str) -> Author:
    name = (name or "").strip() or "Unknown"
    result = await session.execute(select(Author).where(Author.name == name))
    author = result.scalar_one_or_none()
    if author:
        return author
    author = Author(name=name)
    session.add(author)
    await session.flush()
    return author


async def main() -> None:
    csv_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_CSV
    if not csv_path.is_absolute():
        csv_path = REPO_ROOT / csv_path
    if not csv_path.exists():
        print(f"CSV not found: {csv_path}")
        print("Usage: python scripts/import_books_from_csv.py [path/to/books.csv]")
        sys.exit(1)

    async with AsyncSessionLocal() as session:
        created_books = 0
        with open(csv_path, newline="", encoding="utf-8", errors="replace") as f:
            reader = csv.DictReader(f)
            for raw in reader:
                row = _normalize_headers(raw)
                title = _column(row, "title")
                if not title:
                    continue
                isbn_raw = _column(row, "isbn", "isbn13")
                isbn = isbn_raw[:20] if isbn_raw else None
                if isbn and not isbn.isdigit() and not isbn.replace("-", "").isdigit():
                    isbn = None
                if isbn:
                    existing_by_isbn = await session.execute(
                        select(Book).where(Book.isbn == isbn)
                    )
                    if existing_by_isbn.scalar_one_or_none():
                        continue
                authors_str = _column(row, "authors", "author")
                first_author_name = authors_str.split(",")[0].strip() if authors_str else "Unknown"
                author = await get_or_create_author(session, first_author_name)
                pub_date = _parse_date(_column(row, "publication_date", "publication year", "year"))
                genre = _column(row, "genre", "main_genre", "categories")
                avg_rating = _float(_column(row, "average_rating", "rating"))
                ratings_count = _int(_column(row, "ratings_count", "ratings count", "num_ratings"))

                existing = await session.execute(
                    select(Book).where(Book.title == title, Book.author_id == author.id)
                )
                if existing.scalar_one_or_none():
                    continue
                book = Book(
                    title=title[:200],
                    author_id=author.id,
                    isbn=isbn,
                    publication_date=pub_date,
                    main_genre=genre[:100] if genre else None,
                    average_rating=avg_rating,
                    ratings_count=ratings_count,
                )
                session.add(book)
                created_books += 1
        await session.commit()
    print(f"Import complete: {created_books} book(s) from {csv_path.name}.")


if __name__ == "__main__":
    asyncio.run(main())
