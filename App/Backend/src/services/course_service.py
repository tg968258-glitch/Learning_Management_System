from sqlalchemy.orm import Session

from Backend.src.models.course import Course
from Backend.src.models.teacher import Teacher
from Backend.src.repositories.course_repository import CourseRepository
from Backend.src.repositories.teacher_repository import TeacherRepository
from Backend.src.repositories.user_repository import UserRepository
from Backend.src.utils.logger import logger


def get_all_courses(
    db: Session,
    status: str | None = None,
    category: str | None = None
) -> list[Course]:
    return CourseRepository.get_all(db, status=status, category=category)


def get_course(db: Session, course_id: int) -> Course | None:
    return CourseRepository.get_by_id(db, course_id)


def get_course_teachers(db: Session, course_id: int) -> list[Teacher]:
    return CourseRepository.get_teachers_by_course(db, course_id)


def get_teacher_courses(db: Session, teacher_id: int) -> list[Course]:
    return CourseRepository.get_courses_by_teacher(db, teacher_id)


def create_course(
    db: Session,
    course_data: dict,
    created_by_uid: str | None = None
) -> Course:
    if created_by_uid:
        user = UserRepository.get_by_uid(db, created_by_uid)
        if not user:
            raise ValueError("Creator user does not exist")

    course = CourseRepository.create(db, course_data, created_by_uid)
    logger.info(f"Course created in DB: {course.course_id} - {course.course_name}")
    return course


def update_course(
    db: Session,
    course_id: int,
    updated_data: dict
) -> Course | None:
    course = CourseRepository.get_by_id(db, course_id)
    if not course:
        return None

    updated = CourseRepository.update(db, course, updated_data)
    logger.info(f"Course updated: {course_id}")
    return updated


def delete_course(db: Session, course_id: int) -> Course | None:
    course = CourseRepository.get_by_id(db, course_id)
    if not course:
        return None

    CourseRepository.delete(db, course)
    logger.info(f"Course deleted: {course_id}")
    return course


def assign_teachers_to_course(
    db: Session,
    course_id: int,
    teacher_ids: list[int]
) -> list[Teacher]:
    course = CourseRepository.get_by_id(db, course_id)
    if not course:
        raise ValueError("Course not found")

    assigned_teachers = CourseRepository.set_course_teachers(db, course_id, teacher_ids)
    logger.info(f"Teachers assigned to Course {course_id}: {teacher_ids}")
    return assigned_teachers


def publish_course(
    db: Session,
    course_id: int,
    published_by_uid: str
) -> Course:
    course = CourseRepository.get_by_id(db, course_id)
    if not course:
        raise ValueError("Course not found")

    updated = CourseRepository.update(db, course, {
        "status": "active",
        "published_by": published_by_uid
    })
    logger.info(f"Course {course_id} published by {published_by_uid}")
    return updated