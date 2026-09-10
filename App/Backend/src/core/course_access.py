from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from Backend.src.models.course import Course, CourseTeacher
from Backend.src.models.enrollment import Enrollment
from Backend.src.models.student import Student
from Backend.src.models.teacher import Teacher
from Backend.src.models.user import User


def accessible_course_ids(db: Session, user: User) -> set[int] | None:
    """Return accessible course IDs, or None when the user is an admin."""
    if user.role == "admin":
        return None
    if user.role == "student":
        student = db.query(Student).filter(Student.uid == user.uid).first()
        if not student:
            return set()
        return {
            row[0] for row in db.query(Enrollment.course_id).join(
                Course, Course.course_id == Enrollment.course_id
            ).filter(
                Enrollment.student_id == student.student_id,
                Enrollment.status == "active",
                Course.status == "active",
            ).all()
        }
    if user.role == "teacher":
        teacher = db.query(Teacher).filter(Teacher.uid == user.uid).first()
        if not teacher:
            return set()
        return {
            row[0] for row in db.query(CourseTeacher.course_id).filter(
                CourseTeacher.teacher_id == teacher.teacher_id,
            ).all()
        }
    return set()


def require_course_access(db: Session, user: User, course_id: int) -> None:
    allowed = accessible_course_ids(db, user)
    if allowed is not None and course_id not in allowed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this course",
        )


def require_module_access(db: Session, user: User, module_id: int) -> int:
    from Backend.src.models.module import Module

    module = db.query(Module).filter(Module.module_id == module_id).first()
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")
    require_course_access(db, user, module.course_id)
    return module.course_id


def require_lesson_access(db: Session, user: User, lesson_id: int) -> int:
    from Backend.src.models.lesson import Lesson
    from Backend.src.models.module import Module

    row = (
        db.query(Module.course_id)
        .join(Lesson, Lesson.module_id == Module.module_id)
        .filter(Lesson.lesson_id == lesson_id)
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail="Lesson not found")
    require_course_access(db, user, row[0])
    return row[0]


def require_quiz_access(db: Session, user: User, quiz_id: int) -> int:
    from Backend.src.models.quiz import Quiz

    row = db.query(Quiz.course_id).filter(Quiz.quiz_id == quiz_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Quiz not found")
    require_course_access(db, user, row[0])
    return row[0]
