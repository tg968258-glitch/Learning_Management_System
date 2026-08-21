from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from Backend.database import Base


class Lesson(Base):
    __tablename__ = "lessons"

    lesson_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    module_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("modules.module_id"),
        nullable=False
    )

    is_published: Mapped[bool] = mapped_column(
        Boolean,
        default=False
    )

    lesson_title: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )

    created_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )


class LessonContent(Base):
    __tablename__ = "lesson_contents"

    content_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    lesson_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("lessons.lesson_id"),
        nullable=False
    )

    content_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    sequence_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    created_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )


class Resource(Base):
    __tablename__ = "resources"

    resource_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    lesson_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("lessons.lesson_id"),
        nullable=False
    )

    resource_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )

    resource_type: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )

    resource_url: Mapped[str] = mapped_column(
        String(500),
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )