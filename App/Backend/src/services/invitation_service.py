import hashlib
import os
import secrets
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from Backend.src.core.security import hash_password
from Backend.src.repositories.teacher_repository import TeacherRepository
from Backend.src.repositories.user_repository import UserRepository
from Backend.src.services.auth_service import generate_uid
from Backend.src.services.email_service import (
    send_teacher_invite_email,
    send_teacher_welcome_email,
)

INVITE_EXPIRY_HOURS = int(
    os.getenv("TEACHER_INVITE_EXPIRY_HOURS", "48")
)


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def create_teacher_invitation(
    db: Session,
    email: str,
    invited_by_uid: str,
    accept_url_base: str = ""
) -> dict:
    email = email.strip().lower()

    # Check active invitation
    existing = TeacherRepository.get_active_invitation_by_email(db, email)
    if existing:
        raise ValueError(
            "An active invitation already exists for this email. "
            "It will expire in less than 48 hours."
        )

    # Check user existence
    if UserRepository.get_by_email(db, email):
        raise ValueError("A user with this email already exists.")

    # Get admin/inviter name
    inviter = UserRepository.get_by_uid(db, invited_by_uid)
    inviter_name = inviter.username if inviter else "Admin"

    token = secrets.token_urlsafe(48)
    token_hash = _hash_token(token)
    expires_at = datetime.utcnow() + timedelta(hours=INVITE_EXPIRY_HOURS)

    invitation = TeacherRepository.create_invitation(
        db=db,
        email=email,
        token_hash=token_hash,
        expires_at=expires_at,
        invited_by_uid=invited_by_uid
    )

    email_sent = send_teacher_invite_email(
        to_email=email,
        invite_token=token,
        invited_by_name=inviter_name,
        accept_url_base=accept_url_base
    )

    if not email_sent:
        return {
            "message": (
                "Invitation was created, but the invitation email "
                "could not be sent."
            ),
            "invitation_id": invitation.invitation_id,
            "email": email,
            "expires_in_hours": INVITE_EXPIRY_HOURS
        }

    return {
        "message": f"Invitation sent to {email}.",
        "invitation_id": invitation.invitation_id,
        "email": email,
        "expires_in_hours": INVITE_EXPIRY_HOURS
    }


def accept_teacher_invitation(
    db: Session,
    token: str,
    username: str,
    password: str,
    name: str,
    phone_number: str | None = None,
    specialization: str | None = None,
    qualification: str | None = None,
    experience: int | None = None,
) -> dict:
    token_hash = _hash_token(token)
    invitation = TeacherRepository.get_active_invitation_by_token_hash(db, token_hash)

    if not invitation:
        raise ValueError("Invalid or already used invitation token.")

    if invitation.expires_at < datetime.utcnow():
        raise ValueError(
            "This invitation has expired. "
            "Please ask an admin to send a new one."
        )

    if UserRepository.get_by_email(db, invitation.email):
        raise ValueError("A user with this email already exists. Please contact admin.")

    if UserRepository.get_by_username(db, username):
        raise ValueError("Username already taken. Please choose another.")

    uid = generate_uid(db)

    user_data = {
        "uid": uid,
        "username": username,
        "email": invitation.email,
        "recovery_email": None,
        "password_hash": hash_password(password),
        "role": "teacher",
        "email_verified": True,
        "recovery_email_verified": False,
        "is_active": True,
        "deactivated_at": None
    }
    user = UserRepository.create(db, user_data)

    teacher_data = {
        "uid": uid,
        "name": name,
        "phone_number": phone_number,
        "specialization": specialization,
        "qualification": qualification,
        "experience": experience,
    }
    teacher = TeacherRepository.create(db, teacher_data)

    TeacherRepository.mark_invitation_used(db, invitation)

    welcome_email_sent = send_teacher_welcome_email(
        to_email=user.email,
        name=teacher.name,
        username=user.username
    )

    message = "Invitation accepted. Your teacher account has been created."
    if not welcome_email_sent:
        message += " However, the welcome email could not be sent."

    return {
        "message": message,
        "uid": user.uid,
        "username": user.username,
        "email": user.email,
        "role": user.role,
        "email_verified": user.email_verified,
        "teacher_id": teacher.teacher_id
    }