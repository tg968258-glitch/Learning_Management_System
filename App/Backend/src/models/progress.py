from datetime import date

from sqlalchemy import Boolean, Date, ForeignKey, Integer, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from Backend.database import Base


class LessonProgress(Base):
    __tablename__ = "lesson_progress"

    student_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("students.student_id"),
        primary_key=True
    )

    lesson_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("lessons.lesson_id"),
        primary_key=True
    )

    progress_percentage: Mapped[float] = mapped_column(
        Numeric(5, 2),
        default=0
    )

    completed: Mapped[bool] = mapped_column(
        Boolean,
        default=False
    )

    completed_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True
    )