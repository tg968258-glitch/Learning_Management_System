from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, field_validator
from sqlalchemy.orm import Session

from Backend.database import get_db
from Backend.src.core.auth_dependency import get_current_user
from Backend.src.models.user import User
from Backend.src.services.auth_service import (
    authenticate_user,
    logout_user,
    refresh_access_token,
    register_user,
    request_email_verification,
    request_password_reset,
    resend_otp,
    reset_user_password,
    verify_email,
)
from Backend.src.services.invitation_service import accept_teacher_invitation
from Backend.src.utils.input_validator import (
    is_empty,
    is_valid_email,
    validate_length,
)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


# =========================================================
# REGISTER REQUEST
# =========================================================

class RegisterRequest(BaseModel):
    username: str
    email: str
    name: str
    recovery_email: str | None = None
    password: str

    @field_validator("username")
    @classmethod
    def validate_username(cls, value):
        if is_empty(value):
            raise ValueError("Username cannot be empty")
        if not validate_length(value, 3, 50):
            raise ValueError("Username must be between 3 and 50 characters")
        return value

    @field_validator("email")
    @classmethod
    def validate_email(cls, value):
        if is_empty(value):
            raise ValueError("Email cannot be empty")
        if not is_valid_email(value):
            raise ValueError("Invalid email format")
        return value

    @field_validator("name")
    @classmethod
    def validate_name(cls, value):
        value = value.strip()
        if is_empty(value):
            raise ValueError("Name cannot be empty")
        if not validate_length(value, 2, 100):
            raise ValueError("Name must be between 2 and 100 characters")
        return value

    @field_validator("recovery_email")
    @classmethod
    def validate_recovery_email(cls, value):
        if value is None:
            return value
        if is_empty(value):
            return None
        if not is_valid_email(value):
            raise ValueError("Invalid recovery email format")
        return value

    @field_validator("password")
    @classmethod
    def validate_password(cls, value):
        if is_empty(value):
            raise ValueError("Password cannot be empty")
        if not validate_length(value, 8, 100):
            raise ValueError("Password must be between 8 and 100 characters")
        if not any(char.isalpha() for char in value):
            raise ValueError("Password must contain at least one letter")
        if not any(char.isdigit() for char in value):
            raise ValueError("Password must contain at least one number")
        return value


# =========================================================
# LOGIN REQUEST
# =========================================================

class LoginRequest(BaseModel):
    email: str
    password: str
    remember_me: bool = False

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
            raise ValueError("Password must be between 8 and 100 characters")
        return value


class RefreshTokenRequest(BaseModel):
    refresh_token: str

    @field_validator("refresh_token")
    @classmethod
    def validate_refresh_token(cls, value):
        if is_empty(value):
            raise ValueError("Refresh token cannot be empty")
        return value


class LogoutRequest(BaseModel):
    session_id: str

    @field_validator("session_id")
    @classmethod
    def validate_session_id(cls, value):
        if is_empty(value):
            raise ValueError("Session ID cannot be empty")
        return value


# =========================================================
# REGISTER (Student public registration)
# =========================================================

@router.post("/register")
def register(
    request: RegisterRequest,
    db: Session = Depends(get_db)
):
    try:
        return register_user(
            db,
            request.username,
            request.email,
            request.recovery_email,
            request.password,
            request.name,
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


# =========================================================
# LOGIN
# =========================================================

@router.post("/login")
def login(
    request: LoginRequest,
    db: Session = Depends(get_db)
):
    try:
        result = authenticate_user(
            db,
            request.email,
            request.password,
            request.remember_me
        )

    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e)) from e

    if not result:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    return {
        "message": "Login successful",
        **result
    }


# =========================================================
# LOGOUT
# =========================================================

@router.post("/logout")
def logout(
    request: LogoutRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        logout_user(db, request.session_id, current_user.uid)
        return {"message": "Logout successful"}

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/me")
def get_my_profile(
    current_user: User = Depends(get_current_user)
):
    return {
        "uid": current_user.uid,
        "username": current_user.username,
        "email": current_user.email,
        "role": current_user.role,
        "email_verified": current_user.email_verified,
        "is_active": current_user.is_active
    }


# =========================================================
# OTP — Send Verification
# =========================================================

class SendVerificationOTPRequest(BaseModel):
    email: str

    @field_validator("email")
    @classmethod
    def validate_email(cls, value):
        value = value.strip().lower()
        if is_empty(value):
            raise ValueError("Email cannot be empty")
        if not is_valid_email(value):
            raise ValueError("Invalid email format")
        return value


class VerifyEmailOTPRequest(BaseModel):
    email: str
    otp: str

    @field_validator("email")
    @classmethod
    def validate_email(cls, value):
        value = value.strip().lower()
        if is_empty(value):
            raise ValueError("Email cannot be empty")
        if not is_valid_email(value):
            raise ValueError("Invalid email format")
        return value

    @field_validator("otp")
    @classmethod
    def validate_otp(cls, value):
        value = value.strip()
        if not value.isdigit():
            raise ValueError("OTP must contain only digits")
        if len(value) != 6:
            raise ValueError("OTP must be exactly 6 digits")
        return value


@router.post("/send-verification-otp")
def send_verification_otp(
    request: SendVerificationOTPRequest,
    db: Session = Depends(get_db)
):
    try:
        request_email_verification(db, request.email)
        return {
            "message": "Verification OTP sent to your email. It expires in 2 minutes."
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.post("/verify-email")
def verify_email_route(
    request: VerifyEmailOTPRequest,
    db: Session = Depends(get_db)
):
    try:
        verify_email(db, request.email, request.otp)
        return {"message": "Email verified successfully"}

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


# =========================================================
# OTP — Resend
# =========================================================

class ResendOTPRequest(BaseModel):
    email: str
    purpose: str

    @field_validator("email")
    @classmethod
    def validate_email(cls, value):
        value = value.strip().lower()
        if is_empty(value):
            raise ValueError("Email cannot be empty")
        if not is_valid_email(value):
            raise ValueError("Invalid email format")
        return value

    @field_validator("purpose")
    @classmethod
    def validate_purpose(cls, value):
        allowed = [
            "email_verification",
            "password_reset",
            "recovery_email_verification"
        ]
        if value not in allowed:
            raise ValueError(
                f"Purpose must be one of: {', '.join(allowed)}"
            )
        return value


@router.post("/resend-otp")
def resend_otp_endpoint(
    request: ResendOTPRequest,
    db: Session = Depends(get_db)
):
    try:
        resend_otp(db, request.email, request.purpose)
        return {
            "message": "A new OTP has been sent to your email. It expires in 2 minutes."
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


# =========================================================
# FORGOT PASSWORD
# =========================================================

class ForgotPasswordRequest(BaseModel):
    email: str

    @field_validator("email")
    @classmethod
    def validate_email(cls, value):
        value = value.strip().lower()
        if is_empty(value):
            raise ValueError("Email cannot be empty")
        if not is_valid_email(value):
            raise ValueError("Invalid email format")
        return value


class ResetPasswordRequest(BaseModel):
    email: str
    otp: str
    new_password: str

    @field_validator("email")
    @classmethod
    def validate_email(cls, value):
        value = value.strip().lower()
        if is_empty(value):
            raise ValueError("Email cannot be empty")
        if not is_valid_email(value):
            raise ValueError("Invalid email format")
        return value

    @field_validator("otp")
    @classmethod
    def validate_otp(cls, value):
        value = value.strip()
        if not value.isdigit():
            raise ValueError("OTP must contain only digits")
        if len(value) != 6:
            raise ValueError("OTP must be exactly 6 digits")
        return value

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, value):
        if is_empty(value):
            raise ValueError("Password cannot be empty")
        if not validate_length(value, 8, 100):
            raise ValueError("Password must be between 8 and 100 characters")
        if not any(char.isalpha() for char in value):
            raise ValueError("Password must contain at least one letter")
        if not any(char.isdigit() for char in value):
            raise ValueError("Password must contain at least one number")
        return value


@router.post("/forgot-password")
def forgot_password(
    request: ForgotPasswordRequest,
    db: Session = Depends(get_db)
):
    try:
        request_password_reset(db, request.email)
        return {
            "message": "Password reset OTP sent to your email. It expires in 2 minutes."
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.post("/reset-password")
def reset_password(
    request: ResetPasswordRequest,
    db: Session = Depends(get_db)
):
    try:
        reset_user_password(
            db, request.email, request.otp, request.new_password
        )
        return {"message": "Password reset successfully"}

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


# =========================================================
# TOKEN REFRESH
# =========================================================

@router.post("/refresh")
def refresh_token(
    request: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    try:
        access_token = refresh_access_token(db, request.refresh_token)
        return {
            "access_token": access_token,
            "token_type": "bearer"
        }

    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e)) from e


# =========================================================
# ACCEPT TEACHER INVITATION
# =========================================================

class AcceptTeacherInviteRequest(BaseModel):
    token: str
    username: str
    password: str
    name: str
    phone_number: str | None = None
    specialization: str | None = None
    qualification: str | None = None
    experience: int | None = None

    @field_validator("token")
    @classmethod
    def validate_token(cls, value):
        if is_empty(value):
            raise ValueError("Invitation token cannot be empty")
        return value.strip()

    @field_validator("username")
    @classmethod
    def validate_username(cls, value):
        if is_empty(value):
            raise ValueError("Username cannot be empty")
        if not validate_length(value, 3, 50):
            raise ValueError("Username must be between 3 and 50 characters")
        return value

    @field_validator("password")
    @classmethod
    def validate_password(cls, value):
        if is_empty(value):
            raise ValueError("Password cannot be empty")
        if not validate_length(value, 8, 100):
            raise ValueError("Password must be between 8 and 100 characters")
        if not any(char.isalpha() for char in value):
            raise ValueError("Password must contain at least one letter")
        if not any(char.isdigit() for char in value):
            raise ValueError("Password must contain at least one number")
        return value

    @field_validator("name")
    @classmethod
    def validate_name(cls, value):
        value = value.strip()
        if is_empty(value):
            raise ValueError("Name cannot be empty")
        if not validate_length(value, 2, 100):
            raise ValueError("Name must be between 2 and 100 characters")
        return value


@router.post("/accept-teacher-invite")
def accept_teacher_invite(
    request: AcceptTeacherInviteRequest,
    db: Session = Depends(get_db)
):
    try:
        result = accept_teacher_invitation(
            db=db,
            token=request.token,
            username=request.username,
            password=request.password,
            name=request.name,
            phone_number=request.phone_number,
            specialization=request.specialization,
            qualification=request.qualification,
            experience=request.experience,
        )
        return result

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e