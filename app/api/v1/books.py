from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_active_admin
from app.db.session import get_db
from app.models.book import Book
from app.models.review import Review
from app.models.user import User
from app.schemas.book import BookCreate, BookRead, BookUpdate


router = APIRouter()


def _base_books_query() -> Select[tuple[Book]]:
    return select(Book)


@router.get("/", response_model=list[BookRead])
async def list_books(
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    search: str | None = Query(default=None, description="Search by title substring"),
    author_id: int | None = None,
    genre: str | None = None,
    order_by: str = Query("title", description="Sort by: title|rating|ratings_count"),
) -> list[BookRead]:
    query = _base_books_query()
    if search:
        query = query.where(Book.title.ilike(f"%{search}%"))
    if author_id:
        query = query.where(Book.author_id == author_id)
    if genre:
        query = query.where(Book.main_genre == genre)

    if order_by == "rating":
        query = query.order_by(Book.average_rating.desc().nullslast())
    elif order_by == "ratings_count":
        query = query.order_by(Book.ratings_count.desc())
    else:
        query = query.order_by(Book.title.asc())

    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    books = result.scalars().all()
    return [BookRead.model_validate(b) for b in books]


@router.post("/", response_model=BookRead, status_code=status.HTTP_201_CREATED)
async def create_book(
    payload: BookCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_admin),
) -> BookRead:
    book = Book(**payload.model_dump())
    db.add(book)
    await db.commit()
    await db.refresh(book)
    return BookRead.model_validate(book)


@router.get("/{book_id}", response_model=BookRead)
async def get_book(book_id: int, db: AsyncSession = Depends(get_db)) -> BookRead:
    result = await db.execute(select(Book).where(Book.id == book_id))
    book = result.scalar_one_or_none()
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    return BookRead.model_validate(book)


@router.put("/{book_id}", response_model=BookRead)
async def update_book(
    book_id: int,
    payload: BookUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_admin),
) -> BookRead:
    result = await db.execute(select(Book).where(Book.id == book_id))
    book = result.scalar_one_or_none()
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(book, field, value)

    await db.commit()
    await db.refresh(book)
    return BookRead.model_validate(book)


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(
    book_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_admin),
) -> None:
    result = await db.execute(select(Book).where(Book.id == book_id))
    book = result.scalar_one_or_none()
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    await db.delete(book)
    await db.commit()


@router.post("/{book_id}/recalculate-rating", response_model=BookRead)
async def recalculate_book_rating(
    book_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_admin),
) -> BookRead:
    """Recalculate and persist a book's average rating and ratings count based on reviews."""

    result = await db.execute(select(Book).where(Book.id == book_id))
    book = result.scalar_one_or_none()
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")

    stats_query = select(func.count(Review.id), func.avg(Review.rating)).where(Review.book_id == book_id)
    stats_result = await db.execute(stats_query)
    count, avg = stats_result.one()

    book.ratings_count = int(count or 0)
    book.average_rating = float(avg) if avg is not None else None

    await db.commit()
    await db.refresh(book)
    return BookRead.model_validate(book)

