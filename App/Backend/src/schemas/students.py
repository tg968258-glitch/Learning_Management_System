from datetime import date

from pydantic import BaseModel, field_validator

from Backend.src.utils.input_validator import (
    is_alpha,
    is_empty,
    validate_length,
)
from Backend.src.utils.numeric_validator import (
    is_phone_number,
)

class StudentUpdate(BaseModel):
    name: str | None = None
    date_of_birth: date | None = None
    gender: str | None = None
    phone_number: str | None = None

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

    @field_validator("date_of_birth")
    @classmethod
    def validate_date_of_birth(cls, value):
        if value is None:
            return value

        if value >= date.today():
            raise ValueError(
                "Date of birth must be in the past"
            )

        return value

    @field_validator("gender")
    @classmethod
    def validate_gender(cls, value):
        if value is None:
            return value

        value = value.strip()

        if is_empty(value):
            return None

        if not is_alpha(value):
            raise ValueError(
                "Gender must contain only alphabets"
            )

        return value

    @field_validator("phone_number")
    @classmethod
    def validate_phone_number(cls, value):
        if value is None:
            return value

        value = value.strip()

        if is_empty(value):
            return None

        if not is_phone_number(value):
            raise ValueError(
                "Phone number must contain exactly 10 digits"
            )

        return value