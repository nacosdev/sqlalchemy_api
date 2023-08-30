from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import (
    ForeignKey,
)
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, Mapped, mapped_column
from enum import Enum as PyEnum
from uuid import uuid4, UUID
from datetime import datetime, date
import os

database_uri = os.getenv(
    "TEST_DATABASE_URI",
    "postgresql://postgres:postgres@localhost:5432/test_db"
    # "TEST_DATABASE_URI", "sqlite:///testing.db?check_same_thread=False"
)

engine = create_engine(database_uri)  # pragma: no cover


class Base(DeclarativeBase):  # pragma: no cover
    pass


class StatusEnum(PyEnum):  # pragma: no cover
    active = "active"
    inactive = "inactive"
    deleted = "deleted"


class User(Base):  # pragma: no cover
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    active: Mapped[bool] = mapped_column(default=True, nullable=True)
    name: Mapped[str] = mapped_column(nullable=True)
    age: Mapped[int] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(nullable=True)
    updated_at: Mapped[datetime] = mapped_column(nullable=True)
    birthday: Mapped[date] = mapped_column()
    status: Mapped[StatusEnum] = mapped_column(nullable=True)

    def __str__(self):
        return f"<User {self.name}>"


class Post(Base):  # pragma: no cover
    __tablename__ = "posts"
    id: Mapped[int] = mapped_column(primary_key=True)
    content: Mapped[str] = mapped_column()
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))


if "postgres" in engine.url.drivername:

    class Comment(Base):
        __tablename__ = "comments"
        id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
        content: Mapped[str] = mapped_column()
        post_id: Mapped[int] = mapped_column(ForeignKey("posts.id"))

else:

    class Comment(Base):
        __tablename__ = "comments"
        id: Mapped[int] = mapped_column(primary_key=True)
        content: Mapped[str] = mapped_column()
        post_id: Mapped[int] = mapped_column(ForeignKey("posts.id"))


TestSession: Session = sessionmaker(bind=engine)
