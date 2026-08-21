from pydantic import BaseModel, ConfigDict, field_validator

from Backend.src.utils.input_validator import is_empty, validate_length
from Backend.src.utils.numeric_validator import is_positive


class ModuleBase(BaseModel):
    module_name: str
    description: str | None = None
    is_published: bool = False

    @field_validator("module_name")
    @classmethod
    def validate_module_name(cls, value: str) -> str:
        value = value.strip()
        if is_empty(value):
            raise ValueError("Module name cannot be empty")
        if not validate_length(value, 2, 150):
            raise ValueError("Module name must be between 2 and 150 characters")
        return value


class ModuleCreate(ModuleBase):
    course_id: int

    @field_validator("course_id")
    @classmethod
    def validate_course_id(cls, value: int) -> int:
        if not is_positive(value):
            raise ValueError("Course ID must be positive")
        return value


class ModuleUpdate(BaseModel):
    module_name: str | None = None
    description: str | None = None
    is_published: bool | None = None

    @field_validator("module_name")
    @classmethod
    def validate_module_name(cls, value: str | None) -> str | None:
        if value is None:
            return value
        value = value.strip()
        if is_empty(value):
            raise ValueError("Module name cannot be empty")
        if not validate_length(value, 2, 150):
            raise ValueError("Module name must be between 2 and 150 characters")
        return value


class ModuleResponse(BaseModel):
    module_id: int
    course_id: int
    module_name: str
    description: str | None = None
    is_published: bool
    published_by: str | None = None

    model_config = ConfigDict(from_attributes=True)
