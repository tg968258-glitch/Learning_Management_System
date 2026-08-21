from datetime import date

from sqlalchemy.orm import Session

from Backend.src.models.course import Course
from Backend.src.models.enrollment import Enrollment
from Backend.src.models.student import Student
from Backend.src.utils.logger import logger


def get_all_enrollments(
    db: Session,
    status: str | None = None
) -> list[Enrollment]:
    query = db.query(Enrollment)
    if status:
        query = query.filter(Enrollment.status == status)
    return query.all()


def get_enrollment(db: Session, enrollment_id: int) -> Enrollment | None:
    return (
        db.query(Enrollment)
        .filter(Enrollment.enrollment_id == enrollment_id)
        .first()
    )


def get_student_enrollments(
    db: Session,
    student_id: int
) -> list[Enrollment]:
    return (
        db.query(Enrollment)
        .filter(Enrollment.student_id == student_id)
        .all()
    )


def get_course_enrollments(
    db: Session,
    course_id: int
) -> list[Enrollment]:
    return (
        db.query(Enrollment)
        .filter(Enrollment.course_id == course_id)
        .all()
    )


def create_enrollment(
    db: Session,
    student_id: int,
    course_id: int,
    status: str = "active"
) -> Enrollment:
    # Check student existence
    student = db.query(Student).filter(Student.student_id == student_id).first()
    if not student:
        raise ValueError("Student does not exist")

    # Check course existence
    course = db.query(Course).filter(Course.course_id == course_id).first()
    if not course:
        raise ValueError("Course does not exist")

    # Check if already enrolled
    existing = (
        db.query(Enrollment)
        .filter(
            Enrollment.student_id == student_id,
            Enrollment.course_id == course_id
        )
        .first()
    )
    if existing:
        raise ValueError("Student is already enrolled in this course")

    enrollment = Enrollment(
        student_id=student_id,
        course_id=course_id,
        enrollment_date=date.today(),
        status=status
    )

    try:
        db.add(enrollment)
        db.commit()
        db.refresh(enrollment)
        logger.info(f"Student {student_id} enrolled in Course {course_id}")
        return enrollment
    except Exception:
        db.rollback()
        raise


def update_enrollment_status(
    db: Session,
    enrollment_id: int,
    new_status: str
) -> Enrollment | None:
    enrollment = get_enrollment(db, enrollment_id)
    if not enrollment:
        return None

    enrollment.status = new_status

    try:
        db.commit()
        db.refresh(enrollment)
        logger.info(f"Enrollment {enrollment_id} status updated to {new_status}")
        return enrollment
    except Exception:
        db.rollback()
        raise


def delete_enrollment(
    db: Session,
    enrollment_id: int
) -> Enrollment | None:
    enrollment = get_enrollment(db, enrollment_id)
    if not enrollment:
        return None

    try:
        db.delete(enrollment)
        db.commit()
        logger.info(f"Enrollment {enrollment_id} deleted")
        return enrollment
    except Exception:
        db.rollback()
        raise