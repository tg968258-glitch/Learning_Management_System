from datetime import datetime
from sqlalchemy.orm import Session

from Backend.src.models.user import User
from Backend.src.repositories.admin_repository import AdminRepository
from Backend.src.repositories.user_repository import UserRepository
from Backend.src.utils.logger import logger


def get_dashboard_data(db: Session) -> dict:
    return AdminRepository.get_dashboard_metrics(db)


def get_dashboard_stats(db: Session) -> dict:
    return AdminRepository.get_dashboard_stats(db)


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
