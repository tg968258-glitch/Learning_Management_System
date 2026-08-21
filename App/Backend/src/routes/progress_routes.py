from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from Backend.database import get_db
from Backend.src.core.auth_dependency import require_roles
from Backend.src.models.student import Student
from Backend.src.models.user import User
from Backend.src.schemas.progress import (
    CourseProgressSummary,
    LessonProgressResponse,
    LessonProgressUpdate,
)
from Backend.src.services.progress_service import (
    get_course_progress_summary,
    get_lesson_progress,
    update_or_create_lesson_progress,
)

router = APIRouter(
    prefix="/progress",
    tags=["Lesson Progress"]
)


@router.get("/lesson/{lesson_id}", response_model=LessonProgressResponse)
def get_my_lesson_progress(
    lesson_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("student"))
):
    student = db.query(Student).filter(Student.uid == current_user.uid).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found"
        )

    progress = get_lesson_progress(db, student.student_id, lesson_id)
    if not progress:
        return {
            "student_id": student.student_id,
            "lesson_id": lesson_id,
            "progress_percentage": 0.0,
            "completed": False,
            "completed_date": None
        }

    return progress


@router.put("/lesson/{lesson_id}", response_model=LessonProgressResponse)
def record_lesson_progress(
    lesson_id: int,
    progress_in: LessonProgressUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("student"))
):
    student = db.query(Student).filter(Student.uid == current_user.uid).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found"
        )

    try:
        return update_or_create_lesson_progress(
            db=db,
            student_id=student.student_id,
            lesson_id=lesson_id,
            progress_percentage=progress_in.progress_percentage,
            completed=progress_in.completed
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        ) from e


@router.get("/course/{course_id}", response_model=CourseProgressSummary)
def get_my_course_progress(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("student"))
):
    student = db.query(Student).filter(Student.uid == current_user.uid).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found"
        )

    try:
        return get_course_progress_summary(db, student.student_id, course_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        ) from e
