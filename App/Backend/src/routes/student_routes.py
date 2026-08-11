from fastapi import APIRouter, HTTPException
from Backend.src.services.student_service import (
    get_all_students,
    get_student,
    create_student,
    update_student_data,
    remove_student
)

router = APIRouter(prefix="/students", tags=["Students"])


@router.get("/")
def get_students():
    return get_all_students()


@router.get("/{student_id}")
def get_single_student(student_id: int):

    student = get_student(student_id)

    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    return student


@router.post("/")
def add_new_student(student: dict):

    result = create_student(student)

    return {
        "message": "Student added successfully",
        "student": result
    }


@router.put("/{student_id}")
def update_existing_student(
    student_id: int,
    student_data: dict
):

    result = update_student_data(
        student_id,
        student_data
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
def delete_existing_student(student_id: int):

    result = remove_student(student_id)

    if not result:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    return {
        "message": "Student deleted successfully"
    }