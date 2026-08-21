from datetime import datetime

from sqlalchemy.orm import Session

from Backend.src.models.assignment import Assignment
from Backend.src.models.course import Course
from Backend.src.models.enrollment import Enrollment
from Backend.src.models.student import Student
from Backend.src.models.teacher import Teacher
from Backend.src.models.user import User
from Backend.src.utils.logger import logger


def get_dashboard_data(db: Session) -> dict:
    total_users = db.query(User).count()
    total_students = db.query(Student).count()
    total_teachers = db.query(Teacher).count()
    total_courses = db.query(Course).count()
    active_courses = db.query(Course).filter(Course.status == "active").count()
    total_enrollments = db.query(Enrollment).count()
    active_enrollments = db.query(Enrollment).filter(Enrollment.status == "active").count()
    total_assignments = db.query(Assignment).count()

    return {
        "total_users": total_users,
        "total_students": total_students,
        "total_teachers": total_teachers,
        "total_courses": total_courses,
        "active_courses": active_courses,
        "total_enrollments": total_enrollments,
        "active_enrollments": active_enrollments,
        "total_assignments": total_assignments
    }


def get_all_users(
    db: Session,
    role: str | None = None,
    is_active: bool | None = None
) -> list[User]:
    query = db.query(User)
    if role:
        query = query.filter(User.role == role)
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    return query.all()


def toggle_user_active_status(
    db: Session,
    uid: str,
    is_active: bool
) -> User | None:
    user = db.query(User).filter(User.uid == uid).first()
    if not user:
        return None

    user.is_active = is_active
    if not is_active:
        user.deactivated_at = datetime.utcnow()
    else:
        user.deactivated_at = None

    try:
        db.commit()
        db.refresh(user)
        logger.info(f"User {uid} active status set to {is_active}")
        return user
    except Exception:
        db.rollback()
        raise