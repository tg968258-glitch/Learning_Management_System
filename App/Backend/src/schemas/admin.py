from pydantic import BaseModel, field_validator

from Backend.src.utils.input_validator import (
    is_empty,
    is_valid_email,
)


class AdminLoginRequest(BaseModel):
    email: str
    password: str

    @field_validator("email")
    @classmethod
    def validate_email(cls, value):
        value = value.strip().lower()

        if is_empty(value):
            raise ValueError(
                "Email cannot be empty"
            )

        if not is_valid_email(value):
            raise ValueError(
                "Invalid email format"
            )

        return value

    @field_validator("password")
    @classmethod
    def validate_password(cls, value):
        if is_empty(value):
            raise ValueError(
                "Password cannot be empty"
            )

        return value