from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from Backend.database import Base


class Teacher(Base):
    __tablename__ = "teachers"

    teacher_id: Mapped[int] = mapped_column(
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

    phone_number: Mapped[str | None] = mapped_column(
        String(15),
        nullable=True
    )

    specialization: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    qualification: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True
    )

    experience: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )