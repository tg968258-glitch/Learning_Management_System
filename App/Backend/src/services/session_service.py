from sqlalchemy.orm import Session

from Backend.src.models.class_session import ClassSession
from Backend.src.models.course import Course
from Backend.src.models.teacher import Teacher
from Backend.src.utils.logger import logger


def get_sessions_by_course(db: Session, course_id: int) -> list[ClassSession]:
    return (
        db.query(ClassSession)
        .filter(ClassSession.course_id == course_id)
        .order_by(ClassSession.session_date.asc(), ClassSession.start_time.asc())
        .all()
    )


def get_session(db: Session, session_id: int) -> ClassSession | None:
    return db.query(ClassSession).filter(ClassSession.session_id == session_id).first()


def create_session(db: Session, session_data: dict) -> ClassSession:
    course = db.query(Course).filter(Course.course_id == session_data["course_id"]).first()
    if not course:
        raise ValueError("Course does not exist")

    if session_data.get("teacher_id"):
        teacher = db.query(Teacher).filter(Teacher.teacher_id == session_data["teacher_id"]).first()
        if not teacher:
            raise ValueError("Teacher does not exist")

    session = ClassSession(
        course_id=session_data["course_id"],
        teacher_id=session_data.get("teacher_id"),
        session_date=session_data["session_date"],
        start_time=session_data.get("start_time"),
        end_time=session_data.get("end_time"),
        topic=session_data.get("topic")
    )

    try:
        db.add(session)
        db.commit()
        db.refresh(session)
        logger.info(f"Class session scheduled: {session.session_id} for course {session.course_id}")
        return session
    except Exception:
        db.rollback()
        raise


def update_session(db: Session, session_id: int, updated_data: dict) -> ClassSession | None:
    session = get_session(db, session_id)
    if not session:
        return None

    for field, value in updated_data.items():
        if value is not None and hasattr(session, field):
            setattr(session, field, value)

    try:
        db.commit()
        db.refresh(session)
        logger.info(f"Class session updated: {session_id}")
        return session
    except Exception:
        db.rollback()
        raise


def delete_session(db: Session, session_id: int) -> ClassSession | None:
    session = get_session(db, session_id)
    if not session:
        return None

    try:
        db.delete(session)
        db.commit()
        logger.info(f"Class session deleted: {session_id}")
        return session
    except Exception:
        db.rollback()
        raise
