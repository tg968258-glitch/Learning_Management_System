from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from Backend.database import Base


class Course(Base):
    __tablename__ = "courses"

    course_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    course_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    duration: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )

    status: Mapped[str] = mapped_column(
        String(20),
        default="draft"
    )

    category: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    created_by: Mapped[str | None] = mapped_column(
        String(10),
        ForeignKey("users.uid"),
        nullable=True
    )

    published_by: Mapped[str | None] = mapped_column(
        String(10),
        ForeignKey("users.uid"),
        nullable=True
    )

    created_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )


class CourseTeacher(Base):
    __tablename__ = "course_teachers"

    course_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("courses.course_id"),
        primary_key=True
    )

    teacher_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("teachers.teacher_id"),
        primary_key=True
    )

    is_course_admin: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )
