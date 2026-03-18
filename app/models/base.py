from sqlalchemy.orm import DeclarativeBase, declared_attr


class Base(DeclarativeBase):
    """Base class for all ORM models."""

    __abstract__ = True

    @declared_attr.directive
    def __tablename__(cls) -> str:  # type: ignore[misc]
        # Simple automatic table naming convention: lowercase class name + "s"
        return f"{cls.__name__.lower()}s"

