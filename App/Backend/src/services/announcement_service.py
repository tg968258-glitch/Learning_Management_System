from datetime import datetime

from sqlalchemy.orm import Session

from Backend.src.models.announcement import Announcement
from Backend.src.models.class_session import ClassSession
from Backend.src.models.course import Course
from Backend.src.utils.logger import logger


def get_announcements_by_course(db: Session, course_id: int) -> list[Announcement]:
    return (
        db.query(Announcement)
        .filter(Announcement.course_id == course_id)
        .order_by(Announcement.created_at.desc())
        .all()
    )


def get_announcement(db: Session, announcement_id: int) -> Announcement | None:
    return db.query(Announcement).filter(Announcement.announcement_id == announcement_id).first()


def create_announcement(
    db: Session,
    announcement_data: dict,
    created_by_uid: str
) -> Announcement:
    course = db.query(Course).filter(Course.course_id == announcement_data["course_id"]).first()
    if not course:
        raise ValueError("Course does not exist")

    if announcement_data.get("session_id"):
        session = db.query(ClassSession).filter(ClassSession.session_id == announcement_data["session_id"]).first()
        if not session:
            raise ValueError("Class session does not exist")

    announcement = Announcement(
        course_id=announcement_data["course_id"],
        session_id=announcement_data.get("session_id"),
        created_by=created_by_uid,
        title=announcement_data["title"],
        message=announcement_data["message"],
        created_at=datetime.utcnow()
    )

    try:
        db.add(announcement)
        db.commit()
        db.refresh(announcement)
        logger.info(f"Announcement created: {announcement.announcement_id}")
        return announcement
    except Exception:
        db.rollback()
        raise


def update_announcement(
    db: Session,
    announcement_id: int,
    updated_data: dict
) -> Announcement | None:
    announcement = get_announcement(db, announcement_id)
    if not announcement:
        return None

    for field, value in updated_data.items():
        if value is not None and hasattr(announcement, field):
            setattr(announcement, field, value)

    announcement.updated_at = datetime.utcnow()

    try:
        db.commit()
        db.refresh(announcement)
        logger.info(f"Announcement updated: {announcement_id}")
        return announcement
    except Exception:
        db.rollback()
        raise


def delete_announcement(
    db: Session,
    announcement_id: int
) -> Announcement | None:
    announcement = get_announcement(db, announcement_id)
    if not announcement:
        return None

    try:
        db.delete(announcement)
        db.commit()
        logger.info(f"Announcement deleted: {announcement_id}")
        return announcement
    except Exception:
        db.rollback()
        raise
