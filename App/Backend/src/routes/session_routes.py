from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from Backend.database import get_db
from Backend.src.core.auth_dependency import get_current_user, require_roles
from Backend.src.models.course import Course
from Backend.src.models.teacher import Teacher
from Backend.src.models.user import User
from Backend.src.schemas.communication import (
    ClassSessionCreate,
    ClassSessionResponse,
    ClassSessionUpdate,
)
from Backend.src.services.session_service import (
    create_session,
    delete_session,
    get_session,
    get_sessions_by_course,
    update_session,
)

router = APIRouter(
    prefix="/sessions",
    tags=["Class Sessions"]
)


def _build_session_response(db: Session, session) -> dict:
    teacher = db.query(Teacher).filter(Teacher.teacher_id == session.teacher_id).first() if session.teacher_id else None
    course = db.query(Course).filter(Course.course_id == session.course_id).first()
    return {
        "session_id": session.session_id,
        "course_id": session.course_id,
        "teacher_id": session.teacher_id,
        "session_date": session.session_date,
        "start_time": session.start_time,
        "end_time": session.end_time,
        "topic": session.topic,
        "teacher_name": teacher.name if teacher else None,
        "course_name": course.course_name if course else None
    }


@router.get("/course/{course_id}", response_model=list[ClassSessionResponse])
def list_course_sessions(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if course_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Course ID must be positive"
        )
    sessions = get_sessions_by_course(db, course_id)
    return [_build_session_response(db, s) for s in sessions]


@router.get("/{session_id}", response_model=ClassSessionResponse)
def get_single_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if session_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Session ID must be positive"
        )

    session = get_session(db, session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    return _build_session_response(db, session)


@router.post("/", response_model=ClassSessionResponse, status_code=status.HTTP_201_CREATED)
def schedule_class_session(
    session_in: ClassSessionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "teacher"))
):
    try:
        created = create_session(db, session_in.model_dump())
        return _build_session_response(db, created)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        ) from e


@router.put("/{session_id}", response_model=ClassSessionResponse)
def update_class_session(
    session_id: int,
    session_in: ClassSessionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "teacher"))
):
    if session_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Session ID must be positive"
        )

    updated = update_session(db, session_id, session_in.model_dump(exclude_unset=True))
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    return _build_session_response(db, updated)


@router.delete("/{session_id}")
def remove_class_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "teacher"))
):
    if session_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Session ID must be positive"
        )

    deleted = delete_session(db, session_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    return {"message": "Session deleted successfully"}
