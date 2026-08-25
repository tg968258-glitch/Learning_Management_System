from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from Backend.database import get_db
from Backend.src.core.auth_dependency import (
    get_current_user,
    require_roles,
)
from Backend.src.models.user import User
from Backend.src.schemas.teachers import TeacherUpdate
from Backend.src.services.teacher_service import (

    delete_teacher,
    get_all_teachers,
    get_teacher,
    update_teacher,
)

router = APIRouter(
    prefix="/teachers",
    tags=["Teachers"]
)


@router.get("/")
def get_teachers(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles("admin", "teacher")
    )
):
    return get_all_teachers(db)


@router.get("/{teacher_id}")
def get_teacher_by_id(
    teacher_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    )
):
    if teacher_id <= 0:
        raise HTTPException(
            status_code=400,
            detail="Teacher ID must be positive"
        )

    teacher = get_teacher(
        db,
        teacher_id
    )

    if not teacher:
        raise HTTPException(
            status_code=404,
            detail="Teacher not found"
        )

    if (
        current_user.role == "teacher"
        and teacher.uid != current_user.uid
    ):
        raise HTTPException(
            status_code=403,
            detail="You can only view your own teacher profile"
        )

    return teacher



@router.put("/{teacher_id}")
def edit_teacher(
    teacher_id: int,
    teacher: TeacherUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles("admin")
    )
):
    if teacher_id <= 0:
        raise HTTPException(
            status_code=400,
            detail="Teacher ID must be positive"
        )

    updated_teacher = update_teacher(
        db,
        teacher_id,
        teacher.model_dump(
            exclude_unset=True
        )
    )

    if not updated_teacher:
        raise HTTPException(
            status_code=404,
            detail="Teacher not found"
        )

    return {
        "message": "Teacher updated successfully",
        "teacher": updated_teacher
    }


@router.delete("/{teacher_id}")
def remove_teacher(
    teacher_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles("admin")
    )
):
    if teacher_id <= 0:
        raise HTTPException(
            status_code=400,
            detail="Teacher ID must be positive"
        )

    deleted_teacher = delete_teacher(
        db,
        teacher_id
    )

    if not deleted_teacher:
        raise HTTPException(
            status_code=404,
            detail="Teacher not found"
        )

    return {
        "message": "Teacher deleted successfully"
    }