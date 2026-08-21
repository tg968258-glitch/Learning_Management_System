from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from Backend.database import Base


class Notification(Base):
    __tablename__ = "notifications"

    notification_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    uid: Mapped[str] = mapped_column(
        String(10),
        ForeignKey("users.uid"),
        nullable=False
    )

    session_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("class_sessions.session_id"),
        nullable=True
    )

    assignment_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("assignments.assignment_id"),
        nullable=True
    )

    notification_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    title: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True
    )

    message: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    status: Mapped[str] = mapped_column(
        String(20),
        default="pending"
    )

    is_read: Mapped[bool] = mapped_column(
        Boolean,
        default=False
    )

    created_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    sent_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )