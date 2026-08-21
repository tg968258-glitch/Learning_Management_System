from datetime import date, time

from sqlalchemy import Date, ForeignKey, Integer, String, Time
from sqlalchemy.orm import Mapped, mapped_column

from Backend.database import Base


class ClassSession(Base):
    __tablename__ = "class_sessions"

    session_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    course_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("courses.course_id"),
        nullable=False
    )

    teacher_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("teachers.teacher_id"),
        nullable=True
    )

    session_date: Mapped[date] = mapped_column(
        Date,
        nullable=False
    )

    start_time: Mapped[time | None] = mapped_column(
        Time,
        nullable=True
    )

    end_time: Mapped[time | None] = mapped_column(
        Time,
        nullable=True
    )

    topic: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True
    )