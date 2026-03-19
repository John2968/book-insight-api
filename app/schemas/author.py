from pydantic import BaseModel, ConfigDict, Field


class AuthorBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    country: str | None = Field(default=None, max_length=100)
    biography: str | None = None


class AuthorCreate(AuthorBase):
    pass


class AuthorUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=100)
    country: str | None = Field(default=None, max_length=100)
    biography: str | None = None


class AuthorRead(AuthorBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

