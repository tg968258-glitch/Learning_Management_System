from datetime import datetime
from sqlalchemy.orm import Session

from Backend.src.core.security import hash_password
from Backend.src.models.user import User
from Backend.src.repositories.admin_repository import AdminRepository
from Backend.src.repositories.teacher_repository import TeacherRepository
from Backend.src.repositories.user_repository import UserRepository
from Backend.src.services.auth_service import generate_uid
from Backend.src.services.email_service import send_teacher_welcome_email
from Backend.src.utils.logger import logger


def get_dashboard_data(db: Session) -> dict:
    return AdminRepository.get_dashboard_metrics(db)


def get_all_users(
    db: Session,
    role: str | None = None,
    is_active: bool | None = None
) -> list[User]:
    return UserRepository.get_all(db, role=role, is_active=is_active)


def toggle_user_active_status(
    db: Session,
    uid: str,
    is_active: bool
) -> User | None:
    user = UserRepository.get_by_uid(db, uid)
    if not user:
        return None

    update_data = {
        "is_active": is_active,
        "deactivated_at": None if is_active else datetime.utcnow()
    }
    updated = UserRepository.update(db, user, update_data)
    logger.info(f"User {uid} active status set to {is_active}")
    return updated


def create_teacher_directly(
    db: Session,
    email: str,
    username: str,
    password: str,
    name: str,
    phone_number: str | None = None,
    specialization: str | None = None,
    qualification: str | None = None,
    experience: int | None = None,
) -> dict:
    """
    Admin directly creates a teacher user + teacher profile in one atomic operation.
    Sends a welcome email with the temporary password via Brevo.
    """
    email = email.strip().lower()
    username = username.strip()

    # Validate uniqueness
    if UserRepository.get_by_email(db, email):
        raise ValueError("A user with this email already exists.")

    if UserRepository.get_by_username(db, username):
        raise ValueError("Username already taken.")

    uid = generate_uid(db)

    user_data = {
        "uid": uid,
        "username": username,
        "email": email,
        "recovery_email": None,
        "password_hash": hash_password(password),
        "role": "teacher",
        "email_verified": False,
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
    logger.info(f"Admin created teacher directly: uid={uid}, email={email}")

    # Send welcome email with credentials
    send_teacher_welcome_email(
        to_email=email,
        name=name,
        username=username,
        temporary_password=password
    )

    return {
        "message": "Teacher account created successfully. A welcome email has been sent.",
        "uid": user.uid,
        "username": user.username,
        "email": user.email,
        "role": user.role,
        "email_verified": user.email_verified,
        "teacher_id": teacher.teacher_id,
        "name": teacher.name,
        "specialization": teacher.specialization,
        "qualification": getattr(teacher, "qualification", qualification),
        "experience": getattr(teacher, "experience", experience)
    }