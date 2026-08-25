from sqlalchemy.orm import Session

from Backend.src.models.enrollment import Enrollment
from Backend.src.repositories.course_repository import CourseRepository
from Backend.src.repositories.enrollment_repository import EnrollmentRepository
from Backend.src.repositories.student_repository import StudentRepository
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
    return EnrollmentRepository.get_by_id(db, enrollment_id)


def get_student_enrollments(
    db: Session,
    student_id: int
) -> list[Enrollment]:
    return EnrollmentRepository.get_by_student(db, student_id)


def get_course_enrollments(
    db: Session,
    course_id: int
) -> list[Enrollment]:
    return EnrollmentRepository.get_by_course(db, course_id)


def create_enrollment(
    db: Session,
    student_id: int,
    course_id: int,
    status: str = "active"
) -> Enrollment:
    student = StudentRepository.get_by_id(db, student_id)
    if not student:
        raise ValueError("Student does not exist")

    course = CourseRepository.get_by_id(db, course_id)
    if not course:
        raise ValueError("Course does not exist")

    existing = EnrollmentRepository.get_by_student_and_course(db, student_id, course_id)
    if existing:
        raise ValueError("Student is already enrolled in this course")

    enrollment = EnrollmentRepository.create(db, student_id, course_id, status)
    logger.info(f"Student {student_id} enrolled in Course {course_id}")
    return enrollment


def update_enrollment_status(
    db: Session,
    enrollment_id: int,
    new_status: str
) -> Enrollment | None:
    enrollment = EnrollmentRepository.get_by_id(db, enrollment_id)
    if not enrollment:
        return None

    updated = EnrollmentRepository.update_status(db, enrollment, new_status)
    logger.info(f"Enrollment {enrollment_id} status updated to {new_status}")
    return updated


def delete_enrollment(
    db: Session,
    enrollment_id: int
) -> Enrollment | None:
    enrollment = EnrollmentRepository.get_by_id(db, enrollment_id)
    if not enrollment:
        return None

    db.delete(enrollment)
    db.commit()
    logger.info(f"Enrollment {enrollment_id} deleted")
    return enrollment