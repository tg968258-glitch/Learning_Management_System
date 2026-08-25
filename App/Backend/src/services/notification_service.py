from sqlalchemy.orm import Session

from Backend.src.models.notification import Notification
from Backend.src.repositories.notification_repository import NotificationRepository
from Backend.src.repositories.user_repository import UserRepository
from Backend.src.utils.logger import logger


def get_user_notifications(
    db: Session,
    uid: str,
    unread_only: bool = False
) -> list[Notification]:
    return NotificationRepository.get_user_notifications(db, uid, unread_only)


def create_notification(
    db: Session,
    notification_data: dict
) -> Notification:
    user = UserRepository.get_by_uid(db, notification_data["uid"])
    if not user:
        raise ValueError("Recipient user does not exist")

    notification = NotificationRepository.create(db, notification_data)
    logger.info(f"Notification {notification.notification_id} sent to {notification.uid}")
    return notification


def mark_notification_as_read(
    db: Session,
    notification_id: int,
    uid: str
) -> Notification | None:
    notification = NotificationRepository.get_by_id(db, notification_id)
    if not notification:
        return None
    if notification.uid != uid:
        raise ValueError("You can only update your own notifications")

    return NotificationRepository.mark_as_read(db, notification)


def mark_all_notifications_as_read(db: Session, uid: str) -> int:
    return NotificationRepository.mark_all_as_read(db, uid)
