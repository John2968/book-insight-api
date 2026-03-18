from datetime import datetime

from pydantic import BaseModel


class ReadingListEntryBase(BaseModel):
    book_id: int


class ReadingListEntryCreate(ReadingListEntryBase):
    pass


class ReadingListEntryRead(ReadingListEntryBase):
    id: int
    user_id: int
    added_at: datetime

    class Config:
        from_attributes = True

