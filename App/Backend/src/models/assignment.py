from datetime import datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from Backend.database import Base


class Assignment(Base):
    __tablename__ = "assignments"

    assignment_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    course_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("courses.course_id"),
        nullable=False
    )

    module_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("modules.module_id"),
        nullable=False
    )

    title: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    due_date: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False
    )

    max_marks: Mapped[float] = mapped_column(
        Numeric(6, 2),
        nullable=False
    )

    passing_marks: Mapped[float] = mapped_column(
        Numeric(6, 2),
        nullable=False
    )

    created_by: Mapped[str] = mapped_column(
        String(10),
        ForeignKey("users.uid"),
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


class Submission(Base):
    __tablename__ = "submissions"

    __table_args__ = (
        UniqueConstraint(
            "assignment_id",
            "student_id",
            name="uq_assignment_student"
        ),
    )

    submission_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    assignment_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("assignments.assignment_id"),
        nullable=False
    )

    student_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("students.student_id"),
        nullable=False
    )

    submission_date: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

    submission_text: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    submission_file: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True
    )

    status: Mapped[str] = mapped_column(
        String(30),
        default="submitted"
    )

    marks: Mapped[float | None] = mapped_column(
        Numeric(6, 2),
        nullable=True
    )

    graded_by: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("teachers.teacher_id"),
        nullable=True
    )

    feedback: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
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