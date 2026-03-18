from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_active_admin
from app.db.session import get_db
from app.models.author import Author
from app.models.user import User
from app.schemas.author import AuthorCreate, AuthorRead, AuthorUpdate


router = APIRouter()


@router.get("/", response_model=list[AuthorRead])
async def list_authors(
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    search: str | None = Query(default=None, description="Filter authors by name substring"),
) -> list[AuthorRead]:
    query = select(Author)
    if search:
        query = query.where(Author.name.ilike(f"%{search}%"))
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    authors = result.scalars().all()
    return [AuthorRead.model_validate(a) for a in authors]


@router.post("/", response_model=AuthorRead, status_code=status.HTTP_201_CREATED)
async def create_author(
    payload: AuthorCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_admin),
) -> AuthorRead:
    author = Author(**payload.model_dump())
    db.add(author)
    await db.commit()
    await db.refresh(author)
    return AuthorRead.model_validate(author)


@router.get("/{author_id}", response_model=AuthorRead)
async def get_author(author_id: int, db: AsyncSession = Depends(get_db)) -> AuthorRead:
    result = await db.execute(select(Author).where(Author.id == author_id))
    author = result.scalar_one_or_none()
    if not author:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Author not found")
    return AuthorRead.model_validate(author)


@router.put("/{author_id}", response_model=AuthorRead)
async def update_author(
    author_id: int,
    payload: AuthorUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_admin),
) -> AuthorRead:
    result = await db.execute(select(Author).where(Author.id == author_id))
    author = result.scalar_one_or_none()
    if not author:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Author not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(author, field, value)

    await db.commit()
    await db.refresh(author)
    return AuthorRead.model_validate(author)


@router.delete("/{author_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_author(
    author_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_admin),
) -> None:
    result = await db.execute(select(Author).where(Author.id == author_id))
    author = result.scalar_one_or_none()
    if not author:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Author not found")
    await db.delete(author)
    await db.commit()

