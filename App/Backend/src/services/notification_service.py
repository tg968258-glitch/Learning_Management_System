from datetime import datetime

from sqlalchemy.orm import Session

from Backend.src.models.notification import Notification
from Backend.src.models.user import User
from Backend.src.utils.logger import logger


def get_user_notifications(
    db: Session,
    uid: str,
    unread_only: bool = False
) -> list[Notification]:
    query = db.query(Notification).filter(Notification.uid == uid)
    if unread_only:
        query = query.filter(Notification.is_read.is_(False))
    return query.order_by(Notification.created_at.desc()).all()


def create_notification(
    db: Session,
    notification_data: dict
) -> Notification:
    user = db.query(User).filter(User.uid == notification_data["uid"]).first()
    if not user:
        raise ValueError("Recipient user does not exist")

    notification = Notification(
        uid=notification_data["uid"],
        session_id=notification_data.get("session_id"),
        assignment_id=notification_data.get("assignment_id"),
        notification_type=notification_data["notification_type"],
        title=notification_data.get("title"),
        message=notification_data["message"],
        status="sent",
        is_read=False,
        created_at=datetime.utcnow(),
        sent_at=datetime.utcnow()
    )

    try:
        db.add(notification)
        db.commit()
        db.refresh(notification)
        logger.info(f"Notification {notification.notification_id} sent to {notification.uid}")
        return notification
    except Exception:
        db.rollback()
        raise


def mark_notification_as_read(
    db: Session,
    notification_id: int,
    uid: str
) -> Notification | None:
    notification = db.query(Notification).filter(Notification.notification_id == notification_id).first()
    if not notification:
        return None
    if notification.uid != uid:
        raise ValueError("You can only update your own notifications")

    notification.is_read = True
    notification.status = "read"

    try:
        db.commit()
        db.refresh(notification)
        return notification
    except Exception:
        db.rollback()
        raise


def mark_all_notifications_as_read(db: Session, uid: str) -> int:
    try:
        updated_count = (
            db.query(Notification)
            .filter(Notification.uid == uid, Notification.is_read.is_(False))
            .update({"is_read": True, "status": "read"})
        )
        db.commit()
        return updated_count
    except Exception:
        db.rollback()
        raise
