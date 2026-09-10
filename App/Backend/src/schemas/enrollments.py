from datetime import date

from pydantic import BaseModel, ConfigDict, field_validator

from Backend.src.utils.numeric_validator import is_positive


class EnrollmentCreate(BaseModel):
    course_id: int
    model_config = ConfigDict(extra="forbid")

    @field_validator("course_id")
    @classmethod
    def validate_course_id(cls, value: int) -> int:
        if not is_positive(value):
            raise ValueError("Course ID must be a positive integer")
        return value



class EnrollmentResponse(BaseModel):
    enrollment_id: int
    student_id: int
    course_id: int
    enrollment_date: date | None = None
    status: str
    student_name: str | None = None
    student_uid: str | None = None
    student_email: str | None = None
    course_name: str | None = None

    model_config = ConfigDict(from_attributes=True)
