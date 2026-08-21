from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from Backend.database import get_db
from Backend.src.core.auth_dependency import get_current_user, require_roles
from Backend.src.models.user import User
from Backend.src.schemas.notifications import (
    NotificationCreate,
    NotificationResponse,
)
from Backend.src.services.notification_service import (
    create_notification,
    get_user_notifications,
    mark_all_notifications_as_read,
    mark_notification_as_read,
)

router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"]
)


@router.get("/my-notifications", response_model=list[NotificationResponse])
def get_my_notifications(
    unread_only: bool = Query(False, description="Filter unread notifications only"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_user_notifications(db, current_user.uid, unread_only=unread_only)


@router.post("/", response_model=NotificationResponse, status_code=status.HTTP_201_CREATED)
def send_notification(
    notif_in: NotificationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "teacher"))
):
    try:
        return create_notification(db, notif_in.model_dump())
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        ) from e


@router.put("/{notification_id}/read", response_model=NotificationResponse)
def mark_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        updated = mark_notification_as_read(db, notification_id, current_user.uid)
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found"
            )
        return updated
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        ) from e


@router.put("/read-all")
def mark_all_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    count = mark_all_notifications_as_read(db, current_user.uid)
    return {
        "message": f"Marked {count} notifications as read"
    }
