from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from Backend.database import Base


class TeacherInvitation(Base):
    """
    Stores pending teacher invitations created by admin.
    The token is stored as a hash for security.
    """
    __tablename__ = "teacher_invitations"

    invitation_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True
    )

    token_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True
    )

    invited_by: Mapped[str] = mapped_column(
        String(10),
        ForeignKey("users.uid"),
        nullable=False
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False
    )

    is_used: Mapped[bool] = mapped_column(
        Boolean,
        default=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )
