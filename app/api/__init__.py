from fastapi import APIRouter

from app.api.v1 import analytics, auth, authors, books, health, reading_list, reviews

api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(authors.router, prefix="/authors", tags=["authors"])
api_router.include_router(books.router, prefix="/books", tags=["books"])
api_router.include_router(reviews.router, prefix="/reviews", tags=["reviews"])
api_router.include_router(reading_list.router, prefix="/reading-list", tags=["reading-list"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])

