from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ReadingListEntryBase(BaseModel):
    book_id: int


class ReadingListEntryCreate(ReadingListEntryBase):
    pass


class ReadingListEntryRead(ReadingListEntryBase):
    id: int
    user_id: int
    added_at: datetime

    model_config = ConfigDict(from_attributes=True)

