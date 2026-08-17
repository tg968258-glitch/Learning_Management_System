from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, field_validator

from Backend.src.services.auth_service import authenticate_user, register_user
from Backend.src.utils.input_validator import is_empty, is_valid_email, validate_length

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str
    role: str

    @field_validator("username")
    @classmethod
    def validate_username(cls, value):
        if is_empty(value):
            raise ValueError("Username cannot be empty")

        if not validate_length(value, 3, 50):
            raise ValueError(
                "Username must be between 3 and 50 characters"
            )

        return value

    @field_validator("email")
    @classmethod
    def validate_email(cls, value):
        if is_empty(value):
            raise ValueError("Email cannot be empty")

        if not is_valid_email(value):
            raise ValueError("Invalid email format")

        return value

    @field_validator("password")
    @classmethod
    def validate_password(cls, value):
        if is_empty(value):
            raise ValueError("Password cannot be empty")

        if not validate_length(value, 8, 100):
            raise ValueError(
                "Password must be between 8 and 100 characters"
            )

        return value

    @field_validator("role")
    @classmethod
    def validate_role(cls, value):
        if is_empty(value):
            raise ValueError("Role cannot be empty")

        return value


class LoginRequest(BaseModel):
    email: str
    password: str

    @field_validator("email")
    @classmethod
    def validate_email(cls, value):
        if is_empty(value):
            raise ValueError("Email cannot be empty")

        if not is_valid_email(value):
            raise ValueError("Invalid email format")

        return value

    @field_validator("password")
    @classmethod
    def validate_password(cls, value):
        if is_empty(value):
            raise ValueError("Password cannot be empty")

        if not validate_length(value, 8, 100):
            raise ValueError(
                "Password must be between 8 and 100 characters"
            )

        return value


@router.post("/register")
def register(request: RegisterRequest):

    try:
        return register_user(
            request.username,
            request.email,
            request.password,
            request.role
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@router.post("/login")
def login(request: LoginRequest):

    user = authenticate_user(
        request.email,
        request.password
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    return {
        "message": "Login successful",
        "user_id": user["user_id"],
        "username": user["username"],
        "email": user["email"],
        "role": user["role"]
    }