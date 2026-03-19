from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import not_found
from app.core.security import get_current_user
from app.db.session import get_db
from app.models.book import Book
from app.models.review import Review
from app.models.user import User


router = APIRouter()


@router.get("/books/{book_id}/rating-distribution")
async def book_rating_distribution(book_id: int, db: AsyncSession = Depends(get_db)) -> dict:
    # ensure book exists
    book_result = await db.execute(select(Book.id).where(Book.id == book_id))
    if book_result.scalar_one_or_none() is None:
        raise not_found(code="BOOK_NOT_FOUND", message="Book not found", details={"book_id": book_id})

    query = (
        select(Review.rating, func.count(Review.id))
        .where(Review.book_id == book_id)
        .group_by(Review.rating)
        .order_by(Review.rating)
    )
    result = await db.execute(query)
    rows = result.all()
    distribution = {str(rating): count for rating, count in rows}
    return {"book_id": book_id, "distribution": distribution}


@router.get("/genres/top-rated")
async def top_rated_genres(
    db: AsyncSession = Depends(get_db),
    min_ratings: int = Query(10, ge=1, description="Minimum number of ratings to be included"),
    limit: int = Query(10, ge=1, le=50),
) -> list[dict]:
    query = (
        select(
            Book.main_genre,
            func.count(Review.id).label("ratings_count"),
            func.avg(Review.rating).label("avg_rating"),
        )
        .join(Review, Review.book_id == Book.id)
        .where(Book.main_genre.is_not(None))
        .group_by(Book.main_genre)
        .having(func.count(Review.id) >= min_ratings)
        .order_by(func.avg(Review.rating).desc())
        .limit(limit)
    )
    result = await db.execute(query)
    rows = result.all()
    return [
        {"genre": genre, "ratings_count": int(ratings_count or 0), "average_rating": float(avg_rating or 0.0)}
        for genre, ratings_count, avg_rating in rows
    ]


@router.get("/authors/trending")
async def trending_authors(
    db: AsyncSession = Depends(get_db),
    days: int = Query(180, ge=1, le=365, description="Look-back window in days"),
    limit: int = Query(10, ge=1, le=50),
) -> list[dict]:
    window_start = datetime.now(timezone.utc) - timedelta(days=days)
    # compare recent avg rating vs all-time avg rating as a simple "trend" score
    recent_query = (
        select(
            Book.author_id,
            func.avg(Review.rating).label("recent_avg"),
        )
        .join(Review, Review.book_id == Book.id)
        .where(Review.created_at >= window_start)
        .group_by(Book.author_id)
    ).subquery()

    overall_query = (
        select(
            Book.author_id,
            func.avg(Review.rating).label("overall_avg"),
            func.count(Review.id).label("ratings_count"),
        )
        .join(Review, Review.book_id == Book.id)
        .group_by(Book.author_id)
    ).subquery()

    query = (
        select(
            overall_query.c.author_id,
            overall_query.c.ratings_count,
            overall_query.c.overall_avg,
            recent_query.c.recent_avg,
            (recent_query.c.recent_avg - overall_query.c.overall_avg).label("trend_score"),
        )
        .join(
            recent_query,
            recent_query.c.author_id == overall_query.c.author_id,
        )
        .where(overall_query.c.ratings_count >= 10)
        .order_by(func.coalesce((recent_query.c.recent_avg - overall_query.c.overall_avg), 0).desc())
        .limit(limit)
    )
    result = await db.execute(query)
    rows = result.all()
    return [
        {
            "author_id": author_id,
            "ratings_count": int(ratings_count or 0),
            "overall_avg": float(overall_avg or 0.0),
            "recent_avg": float(recent_avg or 0.0),
            "trend_score": float(trend_score or 0.0),
        }
        for author_id, ratings_count, overall_avg, recent_avg, trend_score in rows
    ]


@router.get("/users/me/recommendations")
async def recommend_books_for_me(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = Query(10, ge=1, le=50),
) -> list[dict]:
    """Simple content-based recommendation:

    - find the user's top-rated books
    - collect their main_genres
    - recommend highly-rated books in those genres the user hasn't rated yet
    """

    user_reviews_query = select(Review).where(Review.user_id == current_user.id)
    user_reviews_result = await db.execute(user_reviews_query)
    user_reviews = user_reviews_result.scalars().all()
    if not user_reviews:
        # cold start: recommend globally top-rated books
        query = (
            select(Book)
            .where(Book.ratings_count >= 10)
            .order_by(Book.average_rating.desc().nullslast(), Book.ratings_count.desc())
            .limit(limit)
        )
        result = await db.execute(query)
        books = result.scalars().all()
        return [
            {
                "book_id": b.id,
                "title": b.title,
                "average_rating": b.average_rating,
                "ratings_count": b.ratings_count,
                "main_genre": b.main_genre,
            }
            for b in books
        ]

    # get user's preferred genres based on books they rated >=4
    liked_book_ids = [r.book_id for r in user_reviews if r.rating >= 4]
    if not liked_book_ids:
        liked_book_ids = [r.book_id for r in user_reviews]

    genres_query = (
        select(Book.main_genre, func.count(Book.id))
        .where(Book.id.in_(liked_book_ids), Book.main_genre.is_not(None))
        .group_by(Book.main_genre)
        .order_by(func.count(Book.id).desc())
    )
    genres_result = await db.execute(genres_query)
    preferred_genres = [g for g, _ in genres_result.all()]

    rated_book_ids = [r.book_id for r in user_reviews]

    if preferred_genres:
        rec_query = (
            select(Book)
            .where(
                Book.main_genre.in_(preferred_genres),
                Book.id.not_in(rated_book_ids),
                Book.ratings_count >= 5,
            )
            .order_by(Book.average_rating.desc().nullslast(), Book.ratings_count.desc())
            .limit(limit)
        )
    else:
        rec_query = (
            select(Book)
            .where(
                Book.id.not_in(rated_book_ids),
                Book.ratings_count >= 5,
            )
            .order_by(Book.average_rating.desc().nullslast(), Book.ratings_count.desc())
            .limit(limit)
        )

    rec_result = await db.execute(rec_query)
    books = rec_result.scalars().all()
    return [
        {
            "book_id": b.id,
            "title": b.title,
            "average_rating": b.average_rating,
            "ratings_count": b.ratings_count,
            "main_genre": b.main_genre,
        }
        for b in books
    ]

