from datetime import date

from pydantic import BaseModel, Field


class BookBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    isbn: str | None = Field(default=None, max_length=20)
    publication_date: date | None = None
    description: str | None = None
    cover_image_url: str | None = Field(default=None, max_length=500)
    main_genre: str | None = Field(default=None, max_length=100)
    author_id: int | None = None


class BookCreate(BookBase):
    pass


class BookUpdate(BaseModel):
    title: str | None = Field(default=None, max_length=200)
    isbn: str | None = Field(default=None, max_length=20)
    publication_date: date | None = None
    description: str | None = None
    cover_image_url: str | None = Field(default=None, max_length=500)
    main_genre: str | None = Field(default=None, max_length=100)
    author_id: int | None = None


class BookRead(BookBase):
    id: int
    average_rating: float | None = None
    ratings_count: int

    class Config:
        from_attributes = True

