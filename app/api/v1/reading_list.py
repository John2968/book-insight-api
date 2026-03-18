from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.book import Book
from app.models.reading_list import ReadingListEntry
from app.models.user import User
from app.schemas.reading_list import ReadingListEntryCreate, ReadingListEntryRead


router = APIRouter()


@router.get("/", response_model=list[ReadingListEntryRead])
async def list_my_reading_list(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
) -> list[ReadingListEntryRead]:
    query = (
        select(ReadingListEntry)
        .where(ReadingListEntry.user_id == current_user.id)
        .order_by(ReadingListEntry.added_at.desc())
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(query)
    entries = result.scalars().all()
    return [ReadingListEntryRead.model_validate(e) for e in entries]


@router.post("/", response_model=ReadingListEntryRead, status_code=status.HTTP_201_CREATED)
async def add_to_reading_list(
    payload: ReadingListEntryCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ReadingListEntryRead:
    # ensure book exists
    book_result = await db.execute(select(Book).where(Book.id == payload.book_id))
    book = book_result.scalar_one_or_none()
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")

    # avoid duplicates
    existing_result = await db.execute(
        select(ReadingListEntry).where(
            ReadingListEntry.user_id == current_user.id,
            ReadingListEntry.book_id == payload.book_id,
        )
    )
    existing = existing_result.scalar_one_or_none()
    if existing:
        return ReadingListEntryRead.model_validate(existing)

    entry = ReadingListEntry(user_id=current_user.id, book_id=payload.book_id)
    db.add(entry)
    await db.commit()
    await db.refresh(entry)
    return ReadingListEntryRead.model_validate(entry)


@router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_from_reading_list(
    entry_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    result = await db.execute(select(ReadingListEntry).where(ReadingListEntry.id == entry_id))
    entry = result.scalar_one_or_none()
    if not entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reading list entry not found")
    if entry.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed to remove this entry")

    await db.delete(entry)
    await db.commit()

