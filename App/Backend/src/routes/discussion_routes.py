from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from Backend.database import get_db
from Backend.src.core.auth_dependency import get_current_user
from Backend.src.models.student import Student
from Backend.src.models.teacher import Teacher
from Backend.src.models.user import User
from Backend.src.schemas.communication import (
    DiscussionCreate,
    DiscussionResponse,
    DiscussionUpdate,
)
from Backend.src.services.discussion_service import (
    delete_discussion_message,
    get_course_discussions,
    get_discussion,
    post_discussion,
    update_discussion_message,
)

router = APIRouter(
    prefix="/discussions",
    tags=["Discussions"]
)


def _build_discussion_response(db: Session, d) -> dict:
    user = db.query(User).filter(User.uid == d.sender_uid).first()
    sender_name = user.username if user else None
    if user:
        if user.role == "student":
            student = db.query(Student).filter(Student.uid == user.uid).first()
            if student:
                sender_name = student.name
        elif user.role == "teacher":
            teacher = db.query(Teacher).filter(Teacher.uid == user.uid).first()
            if teacher:
                sender_name = teacher.name

    return {
        "discussion_id": d.discussion_id,
        "course_id": d.course_id,
        "lesson_id": d.lesson_id,
        "sender_uid": d.sender_uid,
        "parent_id": d.parent_id,
        "message": d.message,
        "created_at": d.created_at,
        "updated_at": d.updated_at,
        "sender_name": sender_name,
        "sender_role": user.role if user else None
    }


@router.get("/course/{course_id}", response_model=list[DiscussionResponse])
def list_discussions(
    course_id: int,
    lesson_id: int | None = Query(None, description="Optional lesson filter"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if course_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Course ID must be positive"
        )
    discussions = get_course_discussions(db, course_id, lesson_id=lesson_id)
    return [_build_discussion_response(db, d) for d in discussions]


@router.post("/", response_model=DiscussionResponse, status_code=status.HTTP_201_CREATED)
def post_new_message(
    discussion_in: DiscussionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        created = post_discussion(
            db=db,
            discussion_data=discussion_in.model_dump(),
            sender_uid=current_user.uid
        )
        return _build_discussion_response(db, created)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        ) from e


@router.put("/{discussion_id}", response_model=DiscussionResponse)
def edit_message(
    discussion_id: int,
    discussion_in: DiscussionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        updated = update_discussion_message(
            db=db,
            discussion_id=discussion_id,
            message=discussion_in.message,
            sender_uid=current_user.uid
        )
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Discussion message not found"
            )
        return _build_discussion_response(db, updated)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        ) from e


@router.delete("/{discussion_id}")
def remove_message(
    discussion_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    discussion = get_discussion(db, discussion_id)
    if not discussion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Discussion message not found"
        )

    # Only creator or admin can delete
    if current_user.role != "admin" and discussion.sender_uid != current_user.uid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this message"
        )

    delete_discussion_message(db, discussion_id)
    return {"message": "Discussion message deleted successfully"}
