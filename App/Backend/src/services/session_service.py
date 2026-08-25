from sqlalchemy.orm import Session

from Backend.src.models.class_session import ClassSession
from Backend.src.repositories.course_repository import CourseRepository
from Backend.src.repositories.session_repository import SessionRepository
from Backend.src.repositories.teacher_repository import TeacherRepository
from Backend.src.utils.logger import logger


def get_sessions_by_course(db: Session, course_id: int) -> list[ClassSession]:
    return SessionRepository.get_by_course(db, course_id)


def get_session(db: Session, session_id: int) -> ClassSession | None:
    return SessionRepository.get_by_id(db, session_id)


def create_session(db: Session, session_data: dict) -> ClassSession:
    course = CourseRepository.get_by_id(db, session_data["course_id"])
    if not course:
        raise ValueError("Course does not exist")

    if session_data.get("teacher_id"):
        teacher = TeacherRepository.get_by_id(db, session_data["teacher_id"])
        if not teacher:
            raise ValueError("Teacher does not exist")

    session = SessionRepository.create(db, session_data)
    logger.info(f"Class session scheduled: {session.session_id} for course {session.course_id}")
    return session


def update_session(db: Session, session_id: int, updated_data: dict) -> ClassSession | None:
    session = SessionRepository.get_by_id(db, session_id)
    if not session:
        return None

    updated = SessionRepository.update(db, session, updated_data)
    logger.info(f"Class session updated: {session_id}")
    return updated


def delete_session(db: Session, session_id: int) -> ClassSession | None:
    session = SessionRepository.get_by_id(db, session_id)
    if not session:
        return None

    SessionRepository.delete(db, session)
    logger.info(f"Class session deleted: {session_id}")
    return session
