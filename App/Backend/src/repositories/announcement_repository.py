from datetime import datetime
from sqlalchemy.orm import Session

from Backend.src.models.announcement import Announcement


class AnnouncementRepository:
    @staticmethod
    def get_by_id(db: Session, announcement_id: int) -> Announcement | None:
        return db.query(Announcement).filter(Announcement.announcement_id == announcement_id).first()

    @staticmethod
    def get_by_course(db: Session, course_id: int) -> list[Announcement]:
        return (
            db.query(Announcement)
            .filter(Announcement.course_id == course_id)
            .order_by(Announcement.created_at.desc())
            .all()
        )

    @staticmethod
    def create(db: Session, announcement_data: dict, created_by_uid: str) -> Announcement:
        announcement = Announcement(
            course_id=announcement_data["course_id"],
            session_id=announcement_data.get("session_id"),
            created_by=created_by_uid,
            title=announcement_data["title"],
            message=announcement_data["message"],
            created_at=datetime.utcnow()
        )
        db.add(announcement)
        db.commit()
        db.refresh(announcement)
        return announcement

    @staticmethod
    def update(db: Session, announcement: Announcement, update_data: dict) -> Announcement:
        for field, value in update_data.items():
            if hasattr(announcement, field) and value is not None:
                setattr(announcement, field, value)
        announcement.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(announcement)
        return announcement

    @staticmethod
    def delete(db: Session, announcement: Announcement) -> None:
        db.delete(announcement)
        db.commit()
