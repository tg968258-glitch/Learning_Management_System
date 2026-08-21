from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from Backend.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    audit_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    uid: Mapped[str] = mapped_column(
        String(10),
        ForeignKey("users.uid"),
        nullable=False
    )

    action: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    entity_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    entity_id: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )