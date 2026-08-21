from datetime import date

from sqlalchemy.orm import Session

from Backend.src.models.course import Course
from Backend.src.models.lesson import Lesson
from Backend.src.models.module import Module
from Backend.src.models.progress import LessonProgress
from Backend.src.models.student import Student
from Backend.src.utils.logger import logger


def get_lesson_progress(
    db: Session,
    student_id: int,
    lesson_id: int
) -> LessonProgress | None:
    return (
        db.query(LessonProgress)
        .filter(
            LessonProgress.student_id == student_id,
            LessonProgress.lesson_id == lesson_id
        )
        .first()
    )


def update_or_create_lesson_progress(
    db: Session,
    student_id: int,
    lesson_id: int,
    progress_percentage: float,
    completed: bool
) -> LessonProgress:
    student = db.query(Student).filter(Student.student_id == student_id).first()
    if not student:
        raise ValueError("Student does not exist")

    lesson = db.query(Lesson).filter(Lesson.lesson_id == lesson_id).first()
    if not lesson:
        raise ValueError("Lesson does not exist")

    progress = get_lesson_progress(db, student_id, lesson_id)
    if not progress:
        progress = LessonProgress(
            student_id=student_id,
            lesson_id=lesson_id,
            progress_percentage=progress_percentage,
            completed=completed,
            completed_date=date.today() if completed else None
        )
        db.add(progress)
    else:
        progress.progress_percentage = progress_percentage
        progress.completed = completed
        if completed and not progress.completed_date:
            progress.completed_date = date.today()
        elif not completed:
            progress.completed_date = None

    try:
        db.commit()
        db.refresh(progress)
        logger.info(f"Progress updated: Student {student_id}, Lesson {lesson_id} -> {progress_percentage}%")
        return progress
    except Exception:
        db.rollback()
        raise


def get_course_progress_summary(
    db: Session,
    student_id: int,
    course_id: int
) -> dict:
    course = db.query(Course).filter(Course.course_id == course_id).first()
    if not course:
        raise ValueError("Course does not exist")

    # Get all lesson IDs in this course via modules
    lessons = (
        db.query(Lesson)
        .join(Module, Module.module_id == Lesson.module_id)
        .filter(Module.course_id == course_id)
        .all()
    )
    total_lessons = len(lessons)
    if total_lessons == 0:
        return {
            "course_id": course_id,
            "course_name": course.course_name,
            "total_lessons": 0,
            "completed_lessons": 0,
            "overall_progress_percentage": 0.0
        }

    lesson_ids = [l.lesson_id for l in lessons]
    progress_records = (
        db.query(LessonProgress)
        .filter(
            LessonProgress.student_id == student_id,
            LessonProgress.lesson_id.in_(lesson_ids)
        )
        .all()
    )

    completed_count = sum(1 for p in progress_records if p.completed)
    total_percentage = sum(float(p.progress_percentage) for p in progress_records)
    overall_progress = round(total_percentage / total_lessons, 2)

    return {
        "course_id": course_id,
        "course_name": course.course_name,
        "total_lessons": total_lessons,
        "completed_lessons": completed_count,
        "overall_progress_percentage": overall_progress
    }
