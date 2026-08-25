from sqlalchemy.orm import Session

from Backend.src.models.progress import LessonProgress
from Backend.src.repositories.course_repository import CourseRepository
from Backend.src.repositories.lesson_repository import LessonRepository
from Backend.src.repositories.progress_repository import ProgressRepository
from Backend.src.repositories.student_repository import StudentRepository
from Backend.src.utils.logger import logger


def get_lesson_progress(
    db: Session,
    student_id: int,
    lesson_id: int
) -> LessonProgress | None:
    return ProgressRepository.get_progress(db, student_id, lesson_id)


def update_or_create_lesson_progress(
    db: Session,
    student_id: int,
    lesson_id: int,
    progress_percentage: float,
    completed: bool
) -> LessonProgress:
    student = StudentRepository.get_by_id(db, student_id)
    if not student:
        raise ValueError("Student does not exist")

    lesson = LessonRepository.get_by_id(db, lesson_id)
    if not lesson:
        raise ValueError("Lesson does not exist")

    progress = ProgressRepository.upsert_lesson_progress(
        db=db,
        student_id=student_id,
        lesson_id=lesson_id,
        progress_percentage=progress_percentage,
        completed=completed
    )
    logger.info(f"Progress updated: Student {student_id}, Lesson {lesson_id} -> {progress_percentage}%")
    return progress


def get_course_progress_summary(
    db: Session,
    student_id: int,
    course_id: int
) -> dict:
    course = CourseRepository.get_by_id(db, course_id)
    if not course:
        raise ValueError("Course does not exist")

    lessons = ProgressRepository.get_course_lessons(db, course_id)
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
    progress_records = ProgressRepository.get_student_progress_by_lesson_ids(db, student_id, lesson_ids)

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
