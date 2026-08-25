from datetime import date
from sqlalchemy.orm import Session

from Backend.src.models.lesson import Lesson
from Backend.src.models.module import Module
from Backend.src.models.progress import LessonProgress


class ProgressRepository:
    @staticmethod
    def get_progress(
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

    @staticmethod
    def get_student_progress_by_lesson_ids(
        db: Session,
        student_id: int,
        lesson_ids: list[int]
    ) -> list[LessonProgress]:
        return (
            db.query(LessonProgress)
            .filter(
                LessonProgress.student_id == student_id,
                LessonProgress.lesson_id.in_(lesson_ids)
            )
            .all()
        )

    @staticmethod
    def upsert_lesson_progress(
        db: Session,
        student_id: int,
        lesson_id: int,
        progress_percentage: float,
        completed: bool
    ) -> LessonProgress:
        progress = ProgressRepository.get_progress(db, student_id, lesson_id)
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

        db.commit()
        db.refresh(progress)
        return progress

    @staticmethod
    def get_course_lessons(db: Session, course_id: int) -> list[Lesson]:
        return (
            db.query(Lesson)
            .join(Module, Module.module_id == Lesson.module_id)
            .filter(Module.course_id == course_id)
            .all()
        )
