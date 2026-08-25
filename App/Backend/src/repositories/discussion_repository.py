from datetime import datetime
from sqlalchemy.orm import Session

from Backend.src.models.discussion import Discussion


class DiscussionRepository:
    @staticmethod
    def get_by_id(db: Session, discussion_id: int) -> Discussion | None:
        return db.query(Discussion).filter(Discussion.discussion_id == discussion_id).first()

    @staticmethod
    def get_course_discussions(
        db: Session,
        course_id: int,
        lesson_id: int | None = None
    ) -> list[Discussion]:
        query = db.query(Discussion).filter(Discussion.course_id == course_id)
        if lesson_id:
            query = query.filter(Discussion.lesson_id == lesson_id)
        return query.order_by(Discussion.created_at.asc()).all()

    @staticmethod
    def create(
        db: Session,
        course_id: int,
        sender_uid: str,
        message: str,
        lesson_id: int | None = None,
        parent_id: int | None = None
    ) -> Discussion:
        discussion = Discussion(
            course_id=course_id,
            lesson_id=lesson_id,
            sender_uid=sender_uid,
            parent_id=parent_id,
            message=message,
            created_at=datetime.utcnow()
        )
        db.add(discussion)
        db.commit()
        db.refresh(discussion)
        return discussion

    @staticmethod
    def update_message(db: Session, discussion: Discussion, message: str) -> Discussion:
        discussion.message = message
        discussion.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(discussion)
        return discussion

    @staticmethod
    def delete(db: Session, discussion: Discussion) -> None:
        db.query(Discussion).filter(Discussion.parent_id == discussion.discussion_id).delete()
        db.delete(discussion)
        db.commit()
