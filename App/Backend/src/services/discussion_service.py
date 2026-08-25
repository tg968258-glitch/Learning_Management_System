from sqlalchemy.orm import Session

from Backend.src.models.discussion import Discussion
from Backend.src.repositories.course_repository import CourseRepository
from Backend.src.repositories.discussion_repository import DiscussionRepository
from Backend.src.repositories.lesson_repository import LessonRepository
from Backend.src.utils.logger import logger


def get_course_discussions(
    db: Session,
    course_id: int,
    lesson_id: int | None = None
) -> list[Discussion]:
    return DiscussionRepository.get_course_discussions(db, course_id, lesson_id)


def get_discussion(db: Session, discussion_id: int) -> Discussion | None:
    return DiscussionRepository.get_by_id(db, discussion_id)


def post_discussion(
    db: Session,
    discussion_data: dict,
    sender_uid: str
) -> Discussion:
    course = CourseRepository.get_by_id(db, discussion_data["course_id"])
    if not course:
        raise ValueError("Course does not exist")

    if discussion_data.get("lesson_id"):
        lesson = LessonRepository.get_by_id(db, discussion_data["lesson_id"])
        if not lesson:
            raise ValueError("Lesson does not exist")

    if discussion_data.get("parent_id"):
        parent = DiscussionRepository.get_by_id(db, discussion_data["parent_id"])
        if not parent:
            raise ValueError("Parent discussion message does not exist")

    discussion = DiscussionRepository.create(
        db=db,
        course_id=discussion_data["course_id"],
        sender_uid=sender_uid,
        message=discussion_data["message"],
        lesson_id=discussion_data.get("lesson_id"),
        parent_id=discussion_data.get("parent_id")
    )
    logger.info(f"Discussion posted: {discussion.discussion_id} by {sender_uid}")
    return discussion


def update_discussion_message(
    db: Session,
    discussion_id: int,
    message: str,
    sender_uid: str
) -> Discussion | None:
    discussion = DiscussionRepository.get_by_id(db, discussion_id)
    if not discussion:
        return None
    if discussion.sender_uid != sender_uid:
        raise ValueError("You can only edit your own messages")

    updated = DiscussionRepository.update_message(db, discussion, message)
    logger.info(f"Discussion updated: {discussion_id}")
    return updated


def delete_discussion_message(
    db: Session,
    discussion_id: int
) -> Discussion | None:
    discussion = DiscussionRepository.get_by_id(db, discussion_id)
    if not discussion:
        return None

    DiscussionRepository.delete(db, discussion)
    logger.info(f"Discussion deleted: {discussion_id}")
    return discussion
