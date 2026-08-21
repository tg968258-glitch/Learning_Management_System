from datetime import date

from pydantic import BaseModel, ConfigDict, field_validator

from Backend.src.utils.numeric_validator import is_positive


class EnrollmentCreate(BaseModel):
    course_id: int
    student_id: int | None = None

    @field_validator("course_id")
    @classmethod
    def validate_course_id(cls, value: int) -> int:
        if not is_positive(value):
            raise ValueError("Course ID must be a positive integer")
        return value

    @field_validator("student_id")
    @classmethod
    def validate_student_id(cls, value: int | None) -> int | None:
        if value is not None and not is_positive(value):
            raise ValueError("Student ID must be a positive integer")
        return value


class EnrollmentStatusUpdate(BaseModel):
    status: str

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: str) -> str:
        value = value.strip().lower()
        if value not in ("active", "completed", "dropped", "pending", "rejected"):
            raise ValueError(
                "Status must be one of: active, completed, dropped, pending, rejected"
            )
        return value


class EnrollmentResponse(BaseModel):
    enrollment_id: int
    student_id: int
    course_id: int
    enrollment_date: date | None = None
    status: str
    student_name: str | None = None
    course_name: str | None = None

    model_config = ConfigDict(from_attributes=True)
