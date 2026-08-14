from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, field_validator

from Backend.src.utils.input_validator import (
    is_empty,
    validate_length,
    is_alpha,
    is_valid_email
)

from Backend.src.utils.numeric_validator import (
    is_positive,
    is_phone_number
)

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

class Teacher(BaseModel):
    name: str
    email: str
    phone_number: str
    specialization: str
    qualification: str
    experience: int

class TeacherUpdate(Teacher):
    name: str | None = None
    email: str | None = None
    phone_number: str | None = None
    specialization: str | None = None
    qualification: str | None = None
    experience: int | None = None


    @field_validator("name")
    @classmethod
    def validate_name(cls, value):
        if is_empty(value):
            raise ValueError("Name cannot be empty")

        if not is_alpha(value):
            raise ValueError(
                "Name must contain only alphabets and spaces"
            )

        if not validate_length(value, 2, 100):
            raise ValueError(
                "Name must be between 2 and 100 characters"
            )

        return value

    @field_validator("email")
    @classmethod
    def validate_email(cls, value):
        if is_empty(value):
            raise ValueError("Email cannot be empty")

        if not is_valid_email(value):
            raise ValueError("Invalid email format")

        return value

    @field_validator("phone_number")
    @classmethod
    def validate_phone_number(cls, value):
        if not is_phone_number(value):
            raise ValueError(
                "Phone number must contain exactly 10 digits"
            )

        return value

    @field_validator("specialization")
    @classmethod
    def validate_specialization(cls, value):
        if is_empty(value):
            raise ValueError("Specialization cannot be empty")

        if not validate_length(value, 2, 100):
            raise ValueError(
                "Specialization must be between 2 and 100 characters"
            )

        return value

    @field_validator("qualification")
    @classmethod
    def validate_qualification(cls, value):
        if is_empty(value):
            raise ValueError("Qualification cannot be empty")

        if not validate_length(value, 2, 150):
            raise ValueError(
                "Qualification must be between 2 and 150 characters"
            )

        return value

    @field_validator("experience")
    @classmethod
    def validate_experience(cls, value):
        if not is_positive(value):
            raise ValueError(
                "Experience must be a positive number"
            )

        return value


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
def add_teacher(teacher: Teacher):

    return create_teacher(teacher.model_dump())


# =========================
# UPDATE TEACHER
# =========================

@router.put("/{teacher_id}")
def edit_teacher(
    teacher_id: int,
    teacher: TeacherUpdate
):

    updated_teacher = update_teacher(
        teacher_id,
        teacher.model_dump(exclude_unset=True)
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