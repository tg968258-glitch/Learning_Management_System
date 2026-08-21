from pydantic import BaseModel, field_validator

from Backend.src.utils.input_validator import (
    is_alpha,
    is_empty,
    validate_length,
)
from Backend.src.utils.numeric_validator import (
    is_phone_number,
)


class TeacherCreate(BaseModel):
    uid: str
    name: str
    phone_number: str | None = None
    specialization: str | None = None
    qualification: str | None = None
    experience: int | None = None

    @field_validator("uid")
    @classmethod
    def validate_uid(cls, value):
        value = value.strip()

        if is_empty(value):
            raise ValueError(
                "UID cannot be empty"
            )

        if not validate_length(value, 1, 10):
            raise ValueError(
                "UID must be between 1 and 10 characters"
            )

        return value

    @field_validator("name")
    @classmethod
    def validate_name(cls, value):
        value = value.strip()

        if is_empty(value):
            raise ValueError(
                "Name cannot be empty"
            )

        if not is_alpha(value):
            raise ValueError(
                "Name must contain only alphabets and spaces"
            )

        if not validate_length(value, 2, 100):
            raise ValueError(
                "Name must be between 2 and 100 characters"
            )

        return value

    @field_validator("phone_number")
    @classmethod
    def validate_phone_number(cls, value):
        if value is None:
            return value

        value = value.strip()

        if not is_phone_number(value):
            raise ValueError(
                "Phone number must contain exactly 10 digits"
            )

        return value

    @field_validator("specialization")
    @classmethod
    def validate_specialization(cls, value):
        if value is None:
            return value

        value = value.strip()

        if is_empty(value):
            return None

        if not validate_length(value, 2, 100):
            raise ValueError(
                "Specialization must be between 2 and 100 characters"
            )

        return value

    @field_validator("qualification")
    @classmethod
    def validate_qualification(cls, value):
        if value is None:
            return value

        value = value.strip()

        if is_empty(value):
            return None

        if not validate_length(value, 2, 150):
            raise ValueError(
                "Qualification must be between 2 and 150 characters"
            )

        return value

    @field_validator("experience")
    @classmethod
    def validate_experience(cls, value):
        if value is None:
            return value

        if value < 0:
            raise ValueError(
                "Experience cannot be negative"
            )

        if value > 60:
            raise ValueError(
                "Experience cannot be greater than 60 years"
            )

        return value

class TeacherUpdate(BaseModel):
    name: str | None = None
    phone_number: str | None = None
    specialization: str | None = None
    qualification: str | None = None
    experience: int | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, value):
        if value is None:
            return value

        value = value.strip()

        if is_empty(value):
            raise ValueError(
                "Name cannot be empty"
            )

        if not is_alpha(value):
            raise ValueError(
                "Name must contain only alphabets and spaces"
            )

        if not validate_length(value, 2, 100):
            raise ValueError(
                "Name must be between 2 and 100 characters"
            )

        return value

    @field_validator("phone_number")
    @classmethod
    def validate_phone_number(cls, value):
        if value is None:
            return value

        value = value.strip()

        if not is_phone_number(value):
            raise ValueError(
                "Phone number must contain exactly 10 digits"
            )

        return value

    @field_validator("specialization")
    @classmethod
    def validate_specialization(cls, value):
        if value is None:
            return value

        value = value.strip()

        if is_empty(value):
            return None

        if not validate_length(value, 2, 100):
            raise ValueError(
                "Specialization must be between 2 and 100 characters"
            )

        return value

    @field_validator("qualification")
    @classmethod
    def validate_qualification(cls, value):
        if value is None:
            return value

        value = value.strip()

        if is_empty(value):
            return None

        if not validate_length(value, 2, 150):
            raise ValueError(
                "Qualification must be between 2 and 150 characters"
            )

        return value

    @field_validator("experience")
    @classmethod
    def validate_experience(cls, value):
        if value is None:
            return value

        if value < 0:
            raise ValueError(
                "Experience cannot be negative"
            )

        if value > 60:
            raise ValueError(
                "Experience cannot be greater than 60 years"
            )

        return value