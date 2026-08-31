from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_validator

from Backend.src.utils.input_validator import is_empty, validate_length


class CourseBase(BaseModel):
    course_name: str
    description: str | None = None
    duration: str | None = None
    status: str = "draft"
    category: str | None = None

    @field_validator("course_name")
    @classmethod
    def validate_course_name(cls, value: str) -> str:
        value = value.strip()
        if is_empty(value):
            raise ValueError("Course name cannot be empty")
        if not validate_length(value, 2, 100):
            raise ValueError("Course name must be between 2 and 100 characters")
        return value

    @field_validator("duration")
    @classmethod
    def validate_duration(cls, value: str | None) -> str | None:
        if value is None:
            return value
        value = value.strip()
        if is_empty(value):
            return None
        if not validate_length(value, 1, 50):
            raise ValueError("Duration must be between 1 and 50 characters")
        return value

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: str) -> str:
        value = value.strip().lower()
        if value not in ("active", "inactive", "draft", "archived"):
            raise ValueError("Status must be one of: active, inactive, draft, archived")
        return value

    @field_validator("category")
    @classmethod
    def validate_category(cls, value: str | None) -> str | None:
        if value is None:
            return value
        value = value.strip()
        if is_empty(value):
            return None
        if not validate_length(value, 2, 100):
            raise ValueError("Category must be between 2 and 100 characters")
        return value


class CourseCreate(CourseBase):
    pass


class CourseUpdate(BaseModel):
    course_name: str | None = None
    description: str | None = None
    duration: str | None = None
    status: str | None = None
    category: str | None = None

    @field_validator("course_name")
    @classmethod
    def validate_course_name(cls, value: str | None) -> str | None:
        if value is None:
            return value
        value = value.strip()
        if is_empty(value):
            raise ValueError("Course name cannot be empty")
        if not validate_length(value, 2, 100):
            raise ValueError("Course name must be between 2 and 100 characters")
        return value

    @field_validator("duration")
    @classmethod
    def validate_duration(cls, value: str | None) -> str | None:
        if value is None:
            return value
        value = value.strip()
        if is_empty(value):
            return None
        if not validate_length(value, 1, 50):
            raise ValueError("Duration must be between 1 and 50 characters")
        return value

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: str | None) -> str | None:
        if value is None:
            return value
        value = value.strip().lower()
        if value not in ("active", "inactive", "draft", "archived"):
            raise ValueError("Status must be one of: active, inactive, draft, archived")
        return value

    @field_validator("category")
    @classmethod
    def validate_category(cls, value: str | None) -> str | None:
        if value is None:
            return value
        value = value.strip()
        if is_empty(value):
            return None
        if not validate_length(value, 2, 100):
            raise ValueError("Category must be between 2 and 100 characters")
        return value


class CourseAssignTeachers(BaseModel):
    teacher_ids: list[int]


class CourseTeacherInfo(BaseModel):
    teacher_id: int
    name: str
    specialization: str | None = None

    model_config = ConfigDict(from_attributes=True)


class CourseResponse(BaseModel):
    course_id: int
    course_name: str
    description: str | None = None
    duration: str | None = None
    status: str
    category: str | None = None
    created_by: str | None = None
    teachers: list[CourseTeacherInfo] = []

    model_config = ConfigDict(from_attributes=True)
