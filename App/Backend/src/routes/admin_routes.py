from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from Backend.database import get_db
from Backend.src.core.auth_dependency import require_roles
from Backend.src.models.user import User
from Backend.src.schemas.admin import AdminLoginRequest
from Backend.src.services.admin_service import (
    get_all_users,
    get_dashboard_data,
    toggle_user_active_status,
)
from Backend.src.services.auth_service import authenticate_user

router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)


class UserStatusUpdateRequest(BaseModel):
    is_active: bool


@router.post("/login")
def admin_login(
    request: AdminLoginRequest,
    db: Session = Depends(get_db)
):
    try:
        result = authenticate_user(
            db,
            request.email,
            request.password,
            False
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        ) from e

    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    if result["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access only"
        )

    return {
        "message": "Admin login successful",
        **result
    }


@router.get("/dashboard")
def admin_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin"))
):
    return get_dashboard_data(db)


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
        "is_active": user.is_active,
        "deactivated_at": user.deactivated_at
    }