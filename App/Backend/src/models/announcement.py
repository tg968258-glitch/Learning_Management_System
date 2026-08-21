from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from Backend.database import Base


class Announcement(Base):
    __tablename__ = "announcements"

    announcement_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    course_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("courses.course_id"),
        nullable=False
    )

    session_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("class_sessions.session_id"),
        nullable=True
    )

    created_by: Mapped[str] = mapped_column(
        String(10),
        ForeignKey("users.uid"),
        nullable=False
    )

    title: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )

    message: Mapped[str] = mapped_column(
        Text,
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