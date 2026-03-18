from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import forbidden, not_found
from app.core.security import get_current_user
from app.db.session import get_db
from app.models.book import Book
from app.models.review import Review
from app.models.user import User
from app.schemas.review import ReviewCreate, ReviewRead, ReviewUpdate


router = APIRouter()


@router.get("/", response_model=list[ReviewRead])
async def list_reviews(
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    book_id: int | None = None,
    user_id: int | None = None,
) -> list[ReviewRead]:
    query = select(Review)
    if book_id:
        query = query.where(Review.book_id == book_id)
    if user_id:
        query = query.where(Review.user_id == user_id)
    query = query.order_by(Review.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    reviews = result.scalars().all()
    return [ReviewRead.model_validate(r) for r in reviews]


@router.post("/", response_model=ReviewRead, status_code=status.HTTP_201_CREATED)
async def create_review(
    payload: ReviewCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ReviewRead:
    # ensure book exists
    book_result = await db.execute(select(Book).where(Book.id == payload.book_id))
    book = book_result.scalar_one_or_none()
    if not book:
        raise not_found(code="BOOK_NOT_FOUND", message="Book not found", details={"book_id": payload.book_id})

    review = Review(
        rating=payload.rating,
        review_text=payload.review_text,
        book_id=payload.book_id,
        user_id=current_user.id,
    )
    db.add(review)
    await db.commit()
    await db.refresh(review)

    # update book rating stats
    stats_query = select(func.count(Review.id), func.avg(Review.rating)).where(Review.book_id == payload.book_id)
    stats_result = await db.execute(stats_query)
    count, avg = stats_result.one()
    book.ratings_count = int(count or 0)
    book.average_rating = float(avg) if avg is not None else None
    await db.commit()

    return ReviewRead.model_validate(review)


@router.put("/{review_id}", response_model=ReviewRead)
async def update_review(
    review_id: int,
    payload: ReviewUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ReviewRead:
    result = await db.execute(select(Review).where(Review.id == review_id))
    review = result.scalar_one_or_none()
    if not review:
        raise not_found(code="REVIEW_NOT_FOUND", message="Review not found", details={"review_id": review_id})
    if review.user_id != current_user.id and not current_user.is_admin:
        raise forbidden(code="REVIEW_FORBIDDEN", message="Not allowed to edit this review")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(review, field, value)

    await db.commit()
    await db.refresh(review)

    # refresh book rating stats
    stats_query = select(func.count(Review.id), func.avg(Review.rating)).where(Review.book_id == review.book_id)
    stats_result = await db.execute(stats_query)
    count, avg = stats_result.one()
    book_result = await db.execute(select(Book).where(Book.id == review.book_id))
    book = book_result.scalar_one_or_none()
    if book:
        book.ratings_count = int(count or 0)
        book.average_rating = float(avg) if avg is not None else None
        await db.commit()

    return ReviewRead.model_validate(review)


@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_review(
    review_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    result = await db.execute(select(Review).where(Review.id == review_id))
    review = result.scalar_one_or_none()
    if not review:
        raise not_found(code="REVIEW_NOT_FOUND", message="Review not found", details={"review_id": review_id})
    if review.user_id != current_user.id and not current_user.is_admin:
        raise forbidden(code="REVIEW_FORBIDDEN", message="Not allowed to delete this review")

    book_id = review.book_id
    await db.delete(review)
    await db.commit()

    # refresh book rating stats
    stats_query = select(func.count(Review.id), func.avg(Review.rating)).where(Review.book_id == book_id)
    stats_result = await db.execute(stats_query)
    count, avg = stats_result.one()
    book_result = await db.execute(select(Book).where(Book.id == book_id))
    book = book_result.scalar_one_or_none()
    if book:
        book.ratings_count = int(count or 0)
        book.average_rating = float(avg) if avg is not None else None
        await db.commit()

