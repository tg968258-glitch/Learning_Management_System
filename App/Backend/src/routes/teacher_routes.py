from fastapi import APIRouter, HTTPException

from Backend.src.services.teacher_service import (
    get_all_teachers,
    get_teacher,
    create_teacher,
    update_teacher,
    delete_teacher
)


router = APIRouter(
    prefix="/teachers",
    tags=["Teachers"]
)


# =========================
# GET ALL TEACHERS
# =========================

@router.get("/")
def get_teachers():

    return get_all_teachers()


# =========================
# GET TEACHER BY ID
# =========================

@router.get("/{teacher_id}")
def get_teacher_by_id(teacher_id: int):

    teacher = get_teacher(teacher_id)

    if not teacher:
        raise HTTPException(
            status_code=404,
            detail="Teacher not found"
        )

    return teacher


# =========================
# CREATE TEACHER
# =========================

@router.post("/")
def add_teacher(teacher: dict):

    return create_teacher(teacher)


# =========================
# UPDATE TEACHER
# =========================

@router.put("/{teacher_id}")
def edit_teacher(
    teacher_id: int,
    teacher: dict
):

    updated_teacher = update_teacher(
        teacher_id,
        teacher
    )

    if not updated_teacher:
        raise HTTPException(
            status_code=404,
            detail="Teacher not found"
        )

    return updated_teacher


# =========================
# DELETE TEACHER
# =========================

@router.delete("/{teacher_id}")
def remove_teacher(teacher_id: int):

    deleted_teacher = delete_teacher(
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