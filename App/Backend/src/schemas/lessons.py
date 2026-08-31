from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_validator

from Backend.src.utils.input_validator import is_empty, validate_length
from Backend.src.utils.numeric_validator import is_positive

# =========================================================
# LESSON CONTENT SCHEMAS
# =========================================================

class LessonContentBase(BaseModel):
    content_type: str
    content: str
    sequence_number: int = 1

    @field_validator("content_type")
    @classmethod
    def validate_content_type(cls, value: str) -> str:
        value = value.strip().lower()
        if is_empty(value):
            raise ValueError("Content type cannot be empty")
        if value not in ("text", "video", "markdown", "pdf", "slide", "code", "audio"):
            raise ValueError(
                "Content type must be one of: text, video, markdown, pdf, slide, code, audio"
            )
        return value

    @field_validator("content")
    @classmethod
    def validate_content(cls, value: str) -> str:
        if is_empty(value):
            raise ValueError("Content cannot be empty")
        return value

    @field_validator("sequence_number")
    @classmethod
    def validate_seq(cls, value: int) -> int:
        if value < 1:
            raise ValueError("Sequence number must be at least 1")
        return value


class LessonContentCreate(LessonContentBase):
    lesson_id: int


class LessonContentUpdate(BaseModel):
    content_type: str | None = None
    content: str | None = None
    sequence_number: int | None = None

    @field_validator("content_type")
    @classmethod
    def validate_content_type(cls, value: str | None) -> str | None:
        if value is None:
            return value
        value = value.strip().lower()
        if value not in ("text", "video", "markdown", "pdf", "slide", "code", "audio"):
            raise ValueError(
                "Content type must be one of: text, video, markdown, pdf, slide, code, audio"
            )
        return value


class LessonContentResponse(BaseModel):
    content_id: int
    lesson_id: int
    content_type: str
    content: str
    sequence_number: int

    model_config = ConfigDict(from_attributes=True)


# =========================================================
# RESOURCE SCHEMAS
# =========================================================

class ResourceBase(BaseModel):
    resource_name: str
    resource_type: str | None = None
    resource_url: str

    @field_validator("resource_name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        value = value.strip()
        if is_empty(value):
            raise ValueError("Resource name cannot be empty")
        if not validate_length(value, 2, 150):
            raise ValueError("Resource name must be between 2 and 150 characters")
        return value

    @field_validator("resource_url")
    @classmethod
    def validate_url(cls, value: str) -> str:
        value = value.strip()
        if is_empty(value):
            raise ValueError("Resource URL cannot be empty")
        if not validate_length(value, 5, 500):
            raise ValueError("Resource URL must be between 5 and 500 characters")
        return value


class ResourceCreate(ResourceBase):
    lesson_id: int


class ResourceUpdate(BaseModel):
    resource_name: str | None = None
    resource_type: str | None = None
    resource_url: str | None = None


class ResourceResponse(BaseModel):
    resource_id: int
    lesson_id: int
    resource_name: str
    resource_type: str | None = None
    resource_url: str

    model_config = ConfigDict(from_attributes=True)


# =========================================================
# LESSON SCHEMAS
# =========================================================

class LessonBase(BaseModel):
    lesson_title: str
    is_published: bool = False

    @field_validator("lesson_title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        value = value.strip()
        if is_empty(value):
            raise ValueError("Lesson title cannot be empty")
        if not validate_length(value, 2, 150):
            raise ValueError("Lesson title must be between 2 and 150 characters")
        return value


class LessonCreate(LessonBase):
    module_id: int

    @field_validator("module_id")
    @classmethod
    def validate_module_id(cls, value: int) -> int:
        if not is_positive(value):
            raise ValueError("Module ID must be positive")
        return value


class LessonUpdate(BaseModel):
    lesson_title: str | None = None
    is_published: bool | None = None

    @field_validator("lesson_title")
    @classmethod
    def validate_title(cls, value: str | None) -> str | None:
        if value is None:
            return value
        value = value.strip()
        if is_empty(value):
            raise ValueError("Lesson title cannot be empty")
        if not validate_length(value, 2, 150):
            raise ValueError("Lesson title must be between 2 and 150 characters")
        return value


class LessonResponse(BaseModel):
    lesson_id: int
    module_id: int
    lesson_title: str
    is_published: bool

    model_config = ConfigDict(from_attributes=True)


class LessonDetailResponse(LessonResponse):
    contents: list[LessonContentResponse] = []
    resources: list[ResourceResponse] = []

    model_config = ConfigDict(from_attributes=True)
