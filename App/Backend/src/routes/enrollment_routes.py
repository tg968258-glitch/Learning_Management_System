from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, field_validator
from Backend.src.utils.numeric_validator import is_positive
from Backend.src.services.enrollment_service import (
    get_all_enrollments,
    create_enrollment
)

router = APIRouter(
    prefix="/enrollments",
    tags=["Enrollments"]
)

class Enrollment(BaseModel):
    student_id: int
    course_id: int

    @field_validator("student_id", "course_id")
    @classmethod
    def validate_ids(cls, value):
        if not is_positive(value):
            raise ValueError("ID must be a positive number")
        return value
    
@router.get("/")
def get_enrollments():
    return get_all_enrollments()


@router.post("/")
def add_new_enrollment(
    enrollment: Enrollment
):

    student_id = enrollment.get("student_id")
    course_id = enrollment.get("course_id")


    result = create_enrollment(
        student_id,
        course_id
    )

    if not result["success"]:
        raise HTTPException(
            status_code=404,
            detail=result["message"]
        )

    return result