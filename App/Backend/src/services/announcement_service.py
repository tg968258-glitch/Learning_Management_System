from sqlalchemy.orm import Session

from Backend.src.models.announcement import Announcement
from Backend.src.repositories.announcement_repository import AnnouncementRepository
from Backend.src.repositories.course_repository import CourseRepository
from Backend.src.repositories.session_repository import SessionRepository
from Backend.src.utils.logger import logger


def get_announcements_by_course(db: Session, course_id: int) -> list[Announcement]:
    return AnnouncementRepository.get_by_course(db, course_id)


def get_announcement(db: Session, announcement_id: int) -> Announcement | None:
    return AnnouncementRepository.get_by_id(db, announcement_id)


def create_announcement(
    db: Session,
    announcement_data: dict,
    created_by_uid: str
) -> Announcement:
    course = CourseRepository.get_by_id(db, announcement_data["course_id"])
    if not course:
        raise ValueError("Course does not exist")

    if announcement_data.get("session_id"):
        session = SessionRepository.get_by_id(db, announcement_data["session_id"])
        if not session:
            raise ValueError("Class session does not exist")

    announcement = AnnouncementRepository.create(db, announcement_data, created_by_uid)
    logger.info(f"Announcement created: {announcement.announcement_id}")
    return announcement


def update_announcement(
    db: Session,
    announcement_id: int,
    updated_data: dict
) -> Announcement | None:
    announcement = AnnouncementRepository.get_by_id(db, announcement_id)
    if not announcement:
        return None

    updated = AnnouncementRepository.update(db, announcement, updated_data)
    logger.info(f"Announcement updated: {announcement_id}")
    return updated


def delete_announcement(
    db: Session,
    announcement_id: int
) -> Announcement | None:
    announcement = AnnouncementRepository.get_by_id(db, announcement_id)
    if not announcement:
        return None

    AnnouncementRepository.delete(db, announcement)
    logger.info(f"Announcement deleted: {announcement_id}")
    return announcement
