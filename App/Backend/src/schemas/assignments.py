from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_validator

from Backend.src.utils.input_validator import is_empty, validate_length
from Backend.src.utils.numeric_validator import is_positive


class AssignmentBase(BaseModel):
    title: str
    description: str | None = None
    due_date: datetime
    max_marks: float
    passing_marks: float

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        value = value.strip()
        if is_empty(value):
            raise ValueError("Title cannot be empty")
        if not validate_length(value, 2, 150):
            raise ValueError("Title must be between 2 and 150 characters")
        return value

    @field_validator("max_marks")
    @classmethod
    def validate_max_marks(cls, value: float) -> float:
        if not is_positive(value):
            raise ValueError("Max marks must be positive")
        return round(value, 2)

    @field_validator("passing_marks")
    @classmethod
    def validate_passing_marks(cls, value: float, values) -> float:
        if value < 0:
            raise ValueError("Passing marks cannot be negative")
        return round(value, 2)


class AssignmentCreate(AssignmentBase):
    course_id: int
    module_id: int

    @field_validator("course_id", "module_id")
    @classmethod
    def validate_ids(cls, value: int) -> int:
        if not is_positive(value):
            raise ValueError("ID must be a positive integer")
        return value


class AssignmentUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    due_date: datetime | None = None
    max_marks: float | None = None
    passing_marks: float | None = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str | None) -> str | None:
        if value is None:
            return value
        value = value.strip()
        if is_empty(value):
            raise ValueError("Title cannot be empty")
        if not validate_length(value, 2, 150):
            raise ValueError("Title must be between 2 and 150 characters")
        return value


class SubmissionCreate(BaseModel):
    submission_text: str | None = None
    submission_file: str | None = None

    @field_validator("submission_text", "submission_file")
    @classmethod
    def validate_content(cls, value: str | None) -> str | None:
        if value is not None and is_empty(value):
            return None
        return value


class SubmissionGrade(BaseModel):
    marks: float
    feedback: str | None = None

    @field_validator("marks")
    @classmethod
    def validate_marks(cls, value: float) -> float:
        if value < 0:
            raise ValueError("Marks cannot be negative")
        return round(value, 2)


class SubmissionResponse(BaseModel):
    submission_id: int
    assignment_id: int
    student_id: int
    submission_date: datetime | None = None
    submission_text: str | None = None
    submission_file: str | None = None
    status: str
    marks: float | None = None
    graded_by: int | None = None
    feedback: str | None = None
    student_name: str | None = None

    model_config = ConfigDict(from_attributes=True)


class AssignmentResponse(BaseModel):
    assignment_id: int
    course_id: int
    module_id: int
    title: str
    description: str | None = None
    due_date: datetime
    max_marks: float
    passing_marks: float
    

    model_config = ConfigDict(from_attributes=True)


class AssignmentDetailResponse(AssignmentResponse):
    submissions: list[SubmissionResponse] = []

    model_config = ConfigDict(from_attributes=True)
