import json

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from Backend.database import get_db
from Backend.src.core.auth_dependency import get_current_user, require_roles
from Backend.src.core.cache import CACHE_TTL, redis_client
from Backend.src.core.course_access import accessible_course_ids, require_course_access
from Backend.src.models.announcement import Announcement
from Backend.src.models.enrollment import Enrollment
from Backend.src.models.notification import Notification
from Backend.src.models.student import Student
from Backend.src.models.user import User
from Backend.src.schemas.communication import (
    AnnouncementCreate,
    AnnouncementResponse,
    AnnouncementUpdate,
)
from Backend.src.services.announcement_service import (
    create_announcement,
    delete_announcement,
    get_announcement,
    get_announcements_by_course,
    update_announcement,
)
from Backend.src.services.notification_service import create_notification

router = APIRouter(
    prefix="/announcements",
    tags=["Announcements"]
)


# =========================================================
# CACHE HELPER
# =========================================================

def _clear_announcements_cache():
    """Delete all cached announcement results."""
    keys = redis_client.scan_iter(match="announcements:*")
    deleted_count = 0
    for key in keys:
        redis_client.delete(key)
        deleted_count += 1
    print(f"ANNOUNCEMENTS CACHE CLEARED: {deleted_count} key(s)")


def _build_announcement_response(a) -> dict:
    return {
        "announcement_id": a.announcement_id,
        "course_id": a.course_id,
        "session_id": a.session_id,
        "title": a.title,
        "message": a.message,
        "audience": a.audience,
        "created_by": a.created_by,
        "created_at": a.created_at,
        "updated_at": a.updated_at,
    }
def _can_view_announcement(db: Session, user: User, announcement: Announcement) -> bool:
    if user.role == "admin" or announcement.created_by == user.uid:
        return True
    if user.role != "student":
        return False
    if announcement.course_id is None:
        return True
    allowed = accessible_course_ids(db, user) or set()
    return announcement.course_id in allowed


def _announcement_recipient_uids(db: Session, announcement: Announcement) -> set[str]:
    recipients: set[str] = set()
    query = db.query(Student.uid)
    if announcement.course_id is not None:
        query = query.join(Enrollment, Enrollment.student_id == Student.student_id).filter(
            Enrollment.course_id == announcement.course_id,
            Enrollment.status == "active",
        )
    recipients.update(row[0] for row in query.all())
    return recipients


@router.get("/", response_model=list[AnnouncementResponse])
def list_announcements(
    course_id: int | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Announcement)
    if course_id is not None:
        require_course_access(db, current_user, course_id)
        query = query.filter(Announcement.course_id == course_id)
    return [
        _build_announcement_response(item)
        for item in query.order_by(Announcement.created_at.desc()).all()
        if _can_view_announcement(db, current_user, item)
    ]


@router.get("/course/{course_id}", response_model=list[AnnouncementResponse])
def list_course_announcements(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if course_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Course ID must be positive"
        )

    require_course_access(db, current_user, course_id)

    announcements = get_announcements_by_course(db, course_id)
    return [_build_announcement_response(a) for a in announcements if _can_view_announcement(db, current_user, a)]


@router.get("/{announcement_id}", response_model=AnnouncementResponse)
def get_single_announcement(
    announcement_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if announcement_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Announcement ID must be positive"
        )

    announcement = get_announcement(db, announcement_id)
    if not announcement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Announcement not found"
        )

    if not _can_view_announcement(db, current_user, announcement):
        raise HTTPException(status_code=403, detail="You do not have access to this announcement")
    return _build_announcement_response(announcement)


@router.post("/", response_model=AnnouncementResponse, status_code=status.HTTP_201_CREATED)
def broadcast_announcement(
    announcement_in: AnnouncementCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "teacher"))
):
    try:
        data = announcement_in.model_dump()
        data["audience"] = "course_students" if data.get("course_id") else "students_only"
        if current_user.role == "teacher":
            if not data.get("course_id"):
                raise ValueError("Teachers must select an assigned course")
            require_course_access(db, current_user, data["course_id"])
            data["audience"] = "students_only"
        created = create_announcement(
            db=db,
            announcement_data=data,
            created_by_uid=current_user.uid
        )
        for uid in _announcement_recipient_uids(db, created):
            create_notification(db, {
                "uid": uid,
                "notification_type": "announcement",
                "title": f"New announcement: {created.title}",
                "message": "A new announcement is available. Open it to view the message.",
                "announcement_id": created.announcement_id,
            })
        _clear_announcements_cache()
        return _build_announcement_response(created)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        ) from e


@router.put("/{announcement_id}", response_model=AnnouncementResponse)
def edit_announcement(
    announcement_id: int,
    announcement_in: AnnouncementUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "teacher"))
):
    if announcement_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Announcement ID must be positive"
        )

    updated = update_announcement(
        db=db,
        announcement_id=announcement_id,
        updated_data=announcement_in.model_dump(exclude_unset=True)
    )
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Announcement not found"
        )

    _clear_announcements_cache()
    return _build_announcement_response(updated)


@router.delete("/{announcement_id}")
def remove_announcement(
    announcement_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "teacher"))
):
    if announcement_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Announcement ID must be positive"
        )

    announcement = get_announcement(db, announcement_id)
    if not announcement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Announcement not found"
        )
    if current_user.role == "teacher" and announcement.created_by != current_user.uid:
        raise HTTPException(status_code=403, detail="Teachers can only delete their own announcements")

    db.query(Notification).filter(Notification.announcement_id == announcement_id).delete()
    db.commit()
    delete_announcement(db, announcement_id)

    _clear_announcements_cache()
    return {"message": "Announcement deleted successfully"}
