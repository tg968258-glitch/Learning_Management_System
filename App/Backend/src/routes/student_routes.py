from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from Backend.database import get_db
from Backend.src.core.auth_dependency import (
    get_current_user,
    require_roles,
)
from Backend.src.models.user import User
from Backend.src.schemas.students import (
    StudentCreate,
    StudentUpdate,
)
from Backend.src.services.student_service import (
    create_student,
    delete_student,
    get_all_students,
    get_student,
    update_student,
)

router = APIRouter(
    prefix="/students",
    tags=["Students"]
)


@router.get("/")
def get_students(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles("admin", "teacher")
    )
):
    return get_all_students(db)


@router.get("/{student_id}")
def get_single_student(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    )
):
    if student_id <= 0:
        raise HTTPException(
            status_code=400,
            detail="Student ID must be positive"
        )

    student = get_student(
        db,
        student_id
    )

    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    # Student can only view their own profile
    if (
        current_user.role == "student"
        and student.uid != current_user.uid
    ):
        raise HTTPException(
            status_code=403,
            detail="You can only view your own student profile"
        )

    return student


@router.post("/")
def add_new_student(
    student: StudentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles("admin")
    )
):
    try:
        result = create_student(
            db,
            student.model_dump()
        )

        return {
            "message": "Student added successfully",
            "student": result
        }

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        ) from e


@router.put("/{student_id}")
def update_existing_student(
    student_id: int,
    student_data: StudentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles("admin")
    )
):
    if student_id <= 0:
        raise HTTPException(
            status_code=400,
            detail="Student ID must be positive"
        )

    result = update_student(
        db,
        student_id,
        student_data.model_dump(
            exclude_unset=True
        )
    )

    if not result:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    return {
        "message": "Student updated successfully",
        "student": result
    }


@router.delete("/{student_id}")
def delete_existing_student(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles("admin")
    )
):
    if student_id <= 0:
        raise HTTPException(
            status_code=400,
            detail="Student ID must be positive"
        )

    result = delete_student(
        db,
        student_id
    )

    if not result:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    return {
        "message": "Student deleted successfully"
    }