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

    @field_validator("teacher_ids")
    @classmethod
    def validate_teacher_ids(cls, value: list[int]) -> list[int]:
        if not value:
            raise ValueError("Select at least one teacher")
        if any(teacher_id <= 0 for teacher_id in value):
            raise ValueError("Teacher IDs must be positive integers")
        if len(value) != len(set(value)):
            raise ValueError("Teacher IDs must be unique")
        return value


class CourseTeacherInfo(BaseModel):
    teacher_id: int
    name: str
    specialization: str | None = None

    model_config = ConfigDict(from_attributes=True)


class CourseLessonInfo(BaseModel):
    lesson_id: int
    module_id: int
    lesson_title: str
    is_published: bool


class CourseModuleInfo(BaseModel):
    module_id: int
    course_id: int
    module_name: str
    description: str | None = None
    is_published: bool
    lessons: list[CourseLessonInfo] = []


class CourseResponse(BaseModel):
    course_id: int
    course_name: str
    description: str | None = None
    duration: str | None = None
    status: str
    category: str | None = None
    created_by: str | None = None
    teachers: list[CourseTeacherInfo] = []
    modules: list[CourseModuleInfo] = []
    module_count: int | None = None
    lesson_count: int | None = None
    enrollment_count: int | None = None
    is_enrolled: bool = False
    completed_lessons: int | None = None
    overall_progress_percentage: float | None = None

    model_config = ConfigDict(from_attributes=True)
