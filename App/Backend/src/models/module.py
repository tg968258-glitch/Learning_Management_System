from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from Backend.database import Base


class Module(Base):
    __tablename__ = "modules"

    module_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    course_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("courses.course_id"),
        nullable=False
    )

    is_published: Mapped[bool] = mapped_column(
        Boolean,
        default=False
    )

    published_by: Mapped[str | None] = mapped_column(
        String(10),
        ForeignKey("users.uid"),
        nullable=True
    )

    module_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )