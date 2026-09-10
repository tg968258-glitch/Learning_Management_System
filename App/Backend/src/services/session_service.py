from sqlalchemy.orm import Session

from Backend.src.models.class_session import ClassSession
from Backend.src.models.course import CourseTeacher
from Backend.src.repositories.course_repository import CourseRepository
from Backend.src.repositories.session_repository import SessionRepository
from Backend.src.repositories.teacher_repository import TeacherRepository
from Backend.src.utils.logger import logger


def get_all_sessions(
    db: Session,
    course_id: int | None = None
) -> list[ClassSession]:
    """
    Get all class sessions.

    Optionally filter sessions by course_id.
    """
    return SessionRepository.get_all(
        db,
        course_id=course_id
    )


def get_sessions_by_course(
    db: Session,
    course_id: int
) -> list[ClassSession]:
    """
    Get all sessions belonging to one course.
    """
    return SessionRepository.get_by_course(
        db,
        course_id
    )


def get_session(
    db: Session,
    session_id: int
) -> ClassSession | None:
    """
    Get one session by ID.
    """
    return SessionRepository.get_by_id(
        db,
        session_id
    )


def create_session(
    db: Session,
    session_data: dict
) -> ClassSession:
    """
    Create a class session after validating
    the course and optional teacher.
    """

    # Check that course exists
    course = CourseRepository.get_by_id(
        db,
        session_data["course_id"]
    )

    if not course:
        raise ValueError("Course does not exist")

    # Check teacher if teacher_id was supplied
    teacher_id = session_data.get("teacher_id")

    if teacher_id is not None:
        teacher = TeacherRepository.get_by_id(
            db,
            teacher_id
        )

        if not teacher:
            raise ValueError("Teacher does not exist")

        assigned = db.query(CourseTeacher).filter(
            CourseTeacher.course_id == course.course_id,
            CourseTeacher.teacher_id == teacher_id,
        ).first()
        if not assigned:
            raise ValueError("Teacher is not assigned to this course")

    session = SessionRepository.create(
        db,
        session_data
    )

    logger.info(
        f"Class session scheduled: "
        f"{session.session_id} "
        f"for course {session.course_id}"
    )

    return session


def update_session(
    db: Session,
    session_id: int,
    updated_data: dict
) -> ClassSession | None:
    """
    Update an existing class session.
    """
    session = SessionRepository.get_by_id(
        db,
        session_id
    )

    if not session:
        return None

    # Validate course if course_id is being changed
    if "course_id" in updated_data:
        course = CourseRepository.get_by_id(
            db,
            updated_data["course_id"]
        )

        if not course:
            raise ValueError("Course does not exist")

    # Validate teacher if teacher_id is being changed
    if (
        "teacher_id" in updated_data
        and updated_data["teacher_id"] is not None
    ):
        teacher = TeacherRepository.get_by_id(
            db,
            updated_data["teacher_id"]
        )

        if not teacher:
            raise ValueError("Teacher does not exist")

    updated = SessionRepository.update(
        db,
        session,
        updated_data
    )

    logger.info(
        f"Class session updated: {session_id}"
    )

    return updated


def delete_session(
    db: Session,
    session_id: int
) -> ClassSession | None:
    """
    Delete a class session.
    """
    session = SessionRepository.get_by_id(
        db,
        session_id
    )

    if not session:
        return None

    SessionRepository.delete(
        db,
        session
    )

    logger.info(
        f"Class session deleted: {session_id}"
    )

    return session
