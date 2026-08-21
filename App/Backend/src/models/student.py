from datetime import date

from sqlalchemy import Date, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from Backend.database import Base


class Student(Base):
    __tablename__ = "students"

    student_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    uid: Mapped[str] = mapped_column(
        String(10),
        ForeignKey("users.uid"),
        unique=True,
        nullable=False
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    date_of_birth: Mapped[date | None] = mapped_column(
        Date,
        nullable=True
    )

    gender: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True
    )

    phone_number: Mapped[str | None] = mapped_column(
        String(15),
        nullable=True
    )