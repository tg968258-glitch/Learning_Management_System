from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, field_validator
from sqlalchemy.orm import Session

from Backend.database import get_db
from Backend.src.core.auth_dependency import require_roles
from Backend.src.models.user import User
from Backend.src.services.admin_service import (
    get_all_users,
    get_dashboard_data,
    get_dashboard_stats,
    toggle_user_active_status,
)
from Backend.src.schemas.dashboard import AdminDashboardStats

from Backend.src.services.invitation_service import create_teacher_invitation
from Backend.src.repositories.teacher_repository import TeacherRepository
from Backend.src.utils.input_validator import is_empty, is_valid_email

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


@router.get("/dashboard/stats", response_model=AdminDashboardStats)
def admin_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin"))
):
    return get_dashboard_stats(db)


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


@router.get("/teacher-invitations")
def list_teacher_invitations(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin"))
):
    invitations = TeacherRepository.get_invitations(db)
    return [
        {
            "invitation_id": invite.invitation_id,
            "email": invite.email,
            "status": invite.status,
            "expires_at": invite.expires_at,
            "created_at": invite.created_at,
        }
        for invite in invitations
    ]


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
