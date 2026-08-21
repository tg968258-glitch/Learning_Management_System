from datetime import datetime

from sqlalchemy.orm import Session

from Backend.src.models.course import Course
from Backend.src.models.discussion import Discussion
from Backend.src.models.lesson import Lesson
from Backend.src.utils.logger import logger


def get_course_discussions(
    db: Session,
    course_id: int,
    lesson_id: int | None = None
) -> list[Discussion]:
    query = db.query(Discussion).filter(Discussion.course_id == course_id)
    if lesson_id:
        query = query.filter(Discussion.lesson_id == lesson_id)
    return query.order_by(Discussion.created_at.asc()).all()


def get_discussion(db: Session, discussion_id: int) -> Discussion | None:
    return db.query(Discussion).filter(Discussion.discussion_id == discussion_id).first()


def post_discussion(
    db: Session,
    discussion_data: dict,
    sender_uid: str
) -> Discussion:
    course = db.query(Course).filter(Course.course_id == discussion_data["course_id"]).first()
    if not course:
        raise ValueError("Course does not exist")

    if discussion_data.get("lesson_id"):
        lesson = db.query(Lesson).filter(Lesson.lesson_id == discussion_data["lesson_id"]).first()
        if not lesson:
            raise ValueError("Lesson does not exist")

    if discussion_data.get("parent_id"):
        parent = get_discussion(db, discussion_data["parent_id"])
        if not parent:
            raise ValueError("Parent discussion message does not exist")

    discussion = Discussion(
        course_id=discussion_data["course_id"],
        lesson_id=discussion_data.get("lesson_id"),
        sender_uid=sender_uid,
        parent_id=discussion_data.get("parent_id"),
        message=discussion_data["message"],
        created_at=datetime.utcnow()
    )

    try:
        db.add(discussion)
        db.commit()
        db.refresh(discussion)
        logger.info(f"Discussion posted: {discussion.discussion_id} by {sender_uid}")
        return discussion
    except Exception:
        db.rollback()
        raise


def update_discussion_message(
    db: Session,
    discussion_id: int,
    message: str,
    sender_uid: str
) -> Discussion | None:
    discussion = get_discussion(db, discussion_id)
    if not discussion:
        return None
    if discussion.sender_uid != sender_uid:
        raise ValueError("You can only edit your own messages")

    discussion.message = message
    discussion.updated_at = datetime.utcnow()

    try:
        db.commit()
        db.refresh(discussion)
        logger.info(f"Discussion updated: {discussion_id}")
        return discussion
    except Exception:
        db.rollback()
        raise


def delete_discussion_message(
    db: Session,
    discussion_id: int
) -> Discussion | None:
    discussion = get_discussion(db, discussion_id)
    if not discussion:
        return None

    try:
        # Delete nested replies
        db.query(Discussion).filter(Discussion.parent_id == discussion_id).delete()
        db.delete(discussion)
        db.commit()
        logger.info(f"Discussion deleted: {discussion_id}")
        return discussion
    except Exception:
        db.rollback()
        raise
