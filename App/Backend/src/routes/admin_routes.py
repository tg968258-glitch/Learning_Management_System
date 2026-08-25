from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, field_validator
from sqlalchemy.orm import Session

from Backend.database import get_db
from Backend.src.core.auth_dependency import require_roles
from Backend.src.models.user import User
from Backend.src.services.admin_service import (
    create_teacher_directly,
    get_all_users,
    get_dashboard_data,
    toggle_user_active_status,
)

from Backend.src.services.invitation_service import create_teacher_invitation
from Backend.src.utils.input_validator import is_empty, is_valid_email, validate_length
from Backend.src.utils.numeric_validator import is_phone_number

router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)


class UserStatusUpdateRequest(BaseModel):
    is_active: bool


# =========================================================
# ADMIN DASHBOARD
# =========================================================

@router.get("/dashboard")
def admin_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin"))
):
    return get_dashboard_data(db)


# =========================================================
# LIST USERS
# =========================================================

@router.get("/users")
def list_system_users(
    role: str | None = Query(None, description="Filter by user role"),
    is_active: bool | None = Query(None, description="Filter by active status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin"))
):
    users = get_all_users(db, role=role, is_active=is_active)
    return [
        {
            "uid": u.uid,
            "username": u.username,
            "email": u.email,
            "role": u.role,
            "email_verified": u.email_verified,
            "is_active": u.is_active,
            "deactivated_at": u.deactivated_at
        }
        for u in users
    ]


# =========================================================
# UPDATE USER STATUS
# =========================================================

@router.put("/users/{uid}/status")
def update_user_status(
    uid: str,
    status_req: UserStatusUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin"))
):
    if uid == current_user.uid and not status_req.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Admin cannot deactivate their own account"
        )

    user = toggle_user_active_status(db, uid, status_req.is_active)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return {
        "message": f"User status successfully updated to {'active' if status_req.is_active else 'inactive'}",
        "uid": user.uid,
        "is_active": user.is_active
    }


# =========================================================
# CREATE TEACHER DIRECTLY (Admin creates user + profile)
# =========================================================

class CreateTeacherRequest(BaseModel):
    email: str
    username: str
    password: str
    name: str
    phone_number: str | None = None
    specialization: str | None = None
    qualification: str | None = None
    experience: int | None = None

    @field_validator("email")
    @classmethod
    def validate_email(cls, value):
        value = value.strip().lower()
        if is_empty(value):
            raise ValueError("Email cannot be empty")
        if not is_valid_email(value):
            raise ValueError("Invalid email format")
        return value

    @field_validator("username")
    @classmethod
    def validate_username(cls, value):
        value = value.strip()
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
        if not any(c.isalpha() for c in value):
            raise ValueError("Password must contain at least one letter")
        if not any(c.isdigit() for c in value):
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

    @field_validator("phone_number")
    @classmethod
    def validate_phone(cls, value):
        if value is None:
            return value
        value = value.strip()
        if not is_phone_number(value):
            raise ValueError("Phone number must contain exactly 10 digits")
        return value

    @field_validator("experience")
    @classmethod
    def validate_experience(cls, value):
        if value is None:
            return value
        if value < 0:
            raise ValueError("Experience cannot be negative")
        if value > 60:
            raise ValueError("Experience cannot be greater than 60 years")
        return value


@router.post("/create-teacher")
def create_teacher(
    request: CreateTeacherRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin"))
):
    try:
        result = create_teacher_directly(
            db=db,
            email=request.email,
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
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        ) from e


# =========================================================
# INVITE TEACHER (Admin sends email invitation)
# =========================================================

class InviteTeacherRequest(BaseModel):
    email: str
    accept_url_base: str | None = None   # optional frontend accept URL

    @field_validator("email")
    @classmethod
    def validate_email(cls, value):
        value = value.strip().lower()
        if is_empty(value):
            raise ValueError("Email cannot be empty")
        if not is_valid_email(value):
            raise ValueError("Invalid email format")
        return value


@router.post("/invite-teacher")
def invite_teacher(
    request: InviteTeacherRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin"))
):
    try:
        result = create_teacher_invitation(
            db=db,
            email=request.email,
            invited_by_uid=current_user.uid,
            accept_url_base=request.accept_url_base or ""
        )
        return result

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        ) from e