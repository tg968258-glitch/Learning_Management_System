from datetime import date

from sqlalchemy import Date, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from Backend.database import Base


class Enrollment(Base):
    __tablename__ = "enrollments"

    __table_args__ = (
        UniqueConstraint(
            "student_id",
            "course_id",
            name="uq_student_course"
        ),
    )

    enrollment_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    student_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("students.student_id"),
        nullable=False
    )

    course_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("courses.course_id"),
        nullable=False
    )

    enrollment_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True
    )

    status: Mapped[str] = mapped_column(
        String(20),
        default="active"
    )