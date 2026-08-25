from datetime import datetime
from sqlalchemy.orm import Session

from Backend.src.models.notification import Notification


class NotificationRepository:
    @staticmethod
    def get_by_id(db: Session, notification_id: int) -> Notification | None:
        return db.query(Notification).filter(Notification.notification_id == notification_id).first()

    @staticmethod
    def get_user_notifications(
        db: Session,
        uid: str,
        unread_only: bool = False
    ) -> list[Notification]:
        query = db.query(Notification).filter(Notification.uid == uid)
        if unread_only:
            query = query.filter(Notification.is_read.is_(False))
        return query.order_by(Notification.created_at.desc()).all()

    @staticmethod
    def create(db: Session, notification_data: dict) -> Notification:
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
        db.add(notification)
        db.commit()
        db.refresh(notification)
        return notification

    @staticmethod
    def mark_as_read(db: Session, notification: Notification) -> Notification:
        notification.is_read = True
        notification.status = "read"
        db.commit()
        db.refresh(notification)
        return notification

    @staticmethod
    def mark_all_as_read(db: Session, uid: str) -> int:
        updated_count = (
            db.query(Notification)
            .filter(Notification.uid == uid, Notification.is_read.is_(False))
            .update({"is_read": True, "status": "read"})
        )
        db.commit()
        return updated_count
