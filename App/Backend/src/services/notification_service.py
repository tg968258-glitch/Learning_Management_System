from sqlalchemy.orm import Session

from Backend.src.models.notification import Notification
from Backend.src.models.enrollment import Enrollment
from Backend.src.models.student import Student
from Backend.src.repositories.notification_repository import NotificationRepository
from Backend.src.repositories.user_repository import UserRepository
from Backend.src.utils.logger import logger


def get_user_notifications(
    db: Session,
    uid: str,
    unread_only: bool = False
) -> list[Notification]:
    return NotificationRepository.get_user_notifications(db, uid, unread_only)


def get_unread_notification_count(db: Session, uid: str) -> int:
    return NotificationRepository.count_unread(db, uid)


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


def notify_course_students(
    db: Session,
    course_id: int,
    notification_type: str,
    title: str,
    message: str,
    session_id: int | None = None,
    assignment_id: int | None = None,
) -> int:
    """Create one notification for every actively enrolled student."""
    students = (
        db.query(Student)
        .join(Enrollment, Enrollment.student_id == Student.student_id)
        .filter(
            Enrollment.course_id == course_id,
            Enrollment.status == "active",
        )
        .all()
    )
    for student in students:
        create_notification(db, {
            "uid": student.uid,
            "notification_type": notification_type,
            "title": title,
            "message": message,
            "session_id": session_id,
            "assignment_id": assignment_id,
        })
    return len(students)


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
