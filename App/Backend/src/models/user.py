from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from Backend.database import Base


class User(Base):
    __tablename__ = "users"

    uid: Mapped[str] = mapped_column(
        String(10),
        primary_key=True
    )

    username: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False
    )

    recovery_email: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    role: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )

    email_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False
    )

    recovery_email_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True
    )

    deactivated_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )


class OTPVerification(Base):
    __tablename__ = "otp_verifications"

    otp_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    uid: Mapped[str] = mapped_column(
        String(10),
        ForeignKey("users.uid"),
        nullable=False
    )

    otp_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    purpose: Mapped[str] = mapped_column(
        String(30),
        nullable=False
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False
    )

    attempts: Mapped[int] = mapped_column(
        Integer,
        default=0
    )

    is_used: Mapped[bool] = mapped_column(
        Boolean,
        default=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )


class UserSession(Base):
    __tablename__ = "user_sessions"

    session_id: Mapped[str] = mapped_column(
        String(100),
        primary_key=True
    )

    uid: Mapped[str] = mapped_column(
        String(10),
        ForeignKey("users.uid"),
        nullable=False
    )

    refresh_token_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False
    )

    last_used_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

    revoked: Mapped[bool] = mapped_column(
        Boolean,
        default=False
    )