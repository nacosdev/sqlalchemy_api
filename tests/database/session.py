from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    TIMESTAMP,
    Date,
    Enum,
    ForeignKey,
)
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from enum import Enum as PyEnum
import os


class Base(DeclarativeBase):  # pragma: no cover
    pass


class StatusEnum(PyEnum):  # pragma: no cover
    active = "active"
    inactive = "inactive"
    deleted = "deleted"


class User(Base):  # pragma: no cover
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    active = Column(Boolean, default=True)
    name = Column(String)
    age = Column(Integer, nullable=True)
    created_at = Column(DateTime)
    updated_at = Column(TIMESTAMP)
    birthday = Column(Date, nullable=False)
    status = Column(Enum(StatusEnum))

    def __str__(self):
        return f"<User {self.name}>"


class Post(Base):  # pragma: no cover
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True)
    content = Column(String)
    user_id = Column(ForeignKey("users.id"))


database_uri = os.getenv(
    "TEST_DATABASE_URI",
    "postgresql://postgres:postgres@localhost:5432/test_db"
    # "TEST_DATABASE_URI", sqlite:///testing.db?check_same_thread=False",
)

engine = create_engine(database_uri)  # pragma: no cover

TestSession: Session = sessionmaker(bind=engine)
