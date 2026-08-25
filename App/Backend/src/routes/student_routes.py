from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from Backend.database import get_db
from Backend.src.core.auth_dependency import (
    get_current_user,
    require_roles,
)
from Backend.src.models.user import User
from Backend.src.schemas.students import StudentUpdate
from Backend.src.services.student_service import (
    delete_student,
    get_all_students,
    get_student,
    get_student_by_uid,
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


@router.get("/me")
def get_my_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles("student")
    )
):
    try:
        student = get_student_by_uid(
            db,
            current_user.uid
        )

        return {
            "student": student
        }

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        ) from e


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


@router.put("/me")
def update_my_profile(
    student: StudentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles("student")
    )
):
    try:
        current_student = get_student_by_uid(
            db,
            current_user.uid
        )

        updated_student = update_student(
            db,
            current_student.student_id,
            student.model_dump(
                exclude_unset=True
            )
        )

        return {
            "message": "Profile updated successfully",
            "student": updated_student
        }

    except ValueError as e:
        raise HTTPException(
            status_code=404,
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