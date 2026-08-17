from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, field_validator

from Backend.src.services.student_service import (
    create_student,
    delete_student,
    get_all_students,
    get_student,
    update_student,
)
from Backend.src.utils.input_validator import (
    is_alpha,
    is_empty,
    is_valid_email,
    validate_length,
)
from Backend.src.utils.numeric_validator import in_range, is_phone_number, is_positive

router = APIRouter(
    prefix="/students",
    tags=["Students"]
)


class Student(BaseModel):
    name: str
    age: int
    email: str
    gender: str
    percentage: float
    phone_number: str


    @field_validator("name")
    @classmethod
    def validate_name(cls, value):
        if value is None:
            return value

        if is_empty(value):
            raise ValueError("Name cannot be empty")

        if not is_alpha(value):
            raise ValueError("Name must contain only alphabets and spaces")

        if not validate_length(value, 2, 100):
            raise ValueError("Name must be between 2 and 100 characters")

        return value

    @field_validator("age")
    @classmethod
    def validate_age(cls, value):
        if not is_positive(value):
            raise ValueError("Age must be positive")

        if not in_range(value, 5, 100):
            raise ValueError("Age must be between 5 and 100")

        return value

    @field_validator("email")
    @classmethod
    def validate_email(cls, value):
        if is_empty(value):
            raise ValueError("Email cannot be empty")

        if not is_valid_email(value):
            raise ValueError("Invalid email format")

        return value

    @field_validator("gender")
    @classmethod
    def validate_gender(cls, value):
        if is_empty(value):
            raise ValueError("Gender cannot be empty")

        if not is_alpha(value):
            raise ValueError("Gender must contain only alphabets")

        return value

    @field_validator("percentage")
    @classmethod
    def validate_percentage(cls, value):
        if not in_range(value, 0, 100):
            raise ValueError("Percentage must be between 0 and 100")

        return value

    @field_validator("phone_number")
    @classmethod
    def validate_phone_number(cls, value):
        if not is_phone_number(value):
            raise ValueError("Phone number must contain exactly 10 digits")

        return value

class StudentUpdate(Student):
    name: str | None = None
    age: int | None = None
    email: str | None = None
    gender: str | None = None
    percentage: float | None = None
    phone_number: str | None = None


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
def add_new_student(student: Student):

    result = create_student(student.model_dump())

    return {
        "message": "Student added successfully",
        "student": result
    }


@router.put("/{student_id}")
def update_existing_student(
    student_id: int,
    student_data: StudentUpdate
):
    result = update_student(
        student_id,
        student_data.model_dump(exclude_unset=True)
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

    result = delete_student(student_id)

    if not result:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    return {
        "message": "Student deleted successfully"
    }