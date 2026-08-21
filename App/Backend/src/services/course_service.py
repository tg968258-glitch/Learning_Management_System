from datetime import datetime

from sqlalchemy.orm import Session

from Backend.src.models.course import Course, CourseTeacher
from Backend.src.models.teacher import Teacher
from Backend.src.models.user import User
from Backend.src.utils.logger import logger


def get_all_courses(
    db: Session,
    status: str | None = None,
    category: str | None = None
) -> list[Course]:
    query = db.query(Course)
    if status:
        query = query.filter(Course.status == status)
    if category:
        query = query.filter(Course.category == category)
    return query.all()


def get_course(db: Session, course_id: int) -> Course | None:
    return db.query(Course).filter(Course.course_id == course_id).first()


def get_course_teachers(db: Session, course_id: int) -> list[Teacher]:
    return (
        db.query(Teacher)
        .join(CourseTeacher, CourseTeacher.teacher_id == Teacher.teacher_id)
        .filter(CourseTeacher.course_id == course_id)
        .all()
    )


def get_teacher_courses(db: Session, teacher_id: int) -> list[Course]:
    return (
        db.query(Course)
        .join(CourseTeacher, CourseTeacher.course_id == Course.course_id)
        .filter(CourseTeacher.teacher_id == teacher_id)
        .all()
    )


def create_course(
    db: Session,
    course_data: dict,
    created_by_uid: str | None = None
) -> Course:
    teacher_ids = course_data.pop("teacher_ids", None) or []

    # Validate creator if given
    if created_by_uid:
        user = db.query(User).filter(User.uid == created_by_uid).first()
        if not user:
            raise ValueError("Creator user does not exist")

    course = Course(
        course_name=course_data["course_name"],
        description=course_data.get("description"),
        duration=course_data.get("duration"),
        status=course_data.get("status", "active"),
        category=course_data.get("category"),
        created_by=created_by_uid,
        created_at=datetime.utcnow()
    )

    try:
        db.add(course)
        db.flush()

        # Assign teachers
        if teacher_ids:
            for teacher_id in set(teacher_ids):
                teacher = db.query(Teacher).filter(Teacher.teacher_id == teacher_id).first()
                if not teacher:
                    raise ValueError(f"Teacher with ID {teacher_id} not found")
                db.add(CourseTeacher(course_id=course.course_id, teacher_id=teacher_id))

        db.commit()
        db.refresh(course)
        logger.info(f"Course created in DB: {course.course_id} - {course.course_name}")
        return course

    except Exception:
        db.rollback()
        raise


def update_course(
    db: Session,
    course_id: int,
    updated_data: dict
) -> Course | None:
    course = get_course(db, course_id)
    if not course:
        return None

    for field, value in updated_data.items():
        if value is not None and hasattr(course, field):
            setattr(course, field, value)

    course.updated_at = datetime.utcnow()

    try:
        db.commit()
        db.refresh(course)
        logger.info(f"Course updated: {course_id}")
        return course
    except Exception:
        db.rollback()
        raise


def delete_course(db: Session, course_id: int) -> Course | None:
    course = get_course(db, course_id)
    if not course:
        return None

    try:
        # Remove course_teachers mappings first
        db.query(CourseTeacher).filter(CourseTeacher.course_id == course_id).delete()
        db.delete(course)
        db.commit()
        logger.info(f"Course deleted: {course_id}")
        return course
    except Exception:
        db.rollback()
        raise


def assign_teachers_to_course(
    db: Session,
    course_id: int,
    teacher_ids: list[int]
) -> list[Teacher]:
    course = get_course(db, course_id)
    if not course:
        raise ValueError("Course not found")

    # Clear existing and re-assign
    db.query(CourseTeacher).filter(CourseTeacher.course_id == course_id).delete()

    assigned_teachers = []
    for teacher_id in set(teacher_ids):
        teacher = db.query(Teacher).filter(Teacher.teacher_id == teacher_id).first()
        if not teacher:
            raise ValueError(f"Teacher with ID {teacher_id} not found")
        db.add(CourseTeacher(course_id=course_id, teacher_id=teacher_id))
        assigned_teachers.append(teacher)

    try:
        db.commit()
        logger.info(f"Teachers assigned to Course {course_id}: {teacher_ids}")
        return assigned_teachers
    except Exception:
        db.rollback()
        raise


def publish_course(
    db: Session,
    course_id: int,
    published_by_uid: str
) -> Course:
    course = get_course(db, course_id)
    if not course:
        raise ValueError("Course not found")

    course.status = "active"
    course.published_by = published_by_uid
    course.updated_at = datetime.utcnow()

    try:
        db.commit()
        db.refresh(course)
        logger.info(f"Course {course_id} published by {published_by_uid}")
        return course
    except Exception:
        db.rollback()
        raise