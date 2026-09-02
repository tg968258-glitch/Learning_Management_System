import json

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from Backend.database import get_db
from Backend.src.core.auth_dependency import get_current_user, require_roles
from Backend.src.core.cache import CACHE_TTL, redis_client
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
        "created_by": a.created_by,
        "created_at": a.created_at,
        "updated_at": a.updated_at,
    }


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

    cache_key = f"announcements:course:{course_id}"

    cached = redis_client.get(cache_key)
    if cached:
        print(f"CACHE HIT: {cache_key}")
        return json.loads(cached)

    print(f"CACHE MISS: {cache_key}")
    announcements = get_announcements_by_course(db, course_id)
    response = [_build_announcement_response(a) for a in announcements]

    redis_client.setex(
        cache_key,
        CACHE_TTL,
        json.dumps(response, default=str)
    )
    print(f"CACHE CREATED: {cache_key}")
    return response


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

    cache_key = f"announcements:{announcement_id}"

    cached = redis_client.get(cache_key)
    if cached:
        print(f"CACHE HIT: {cache_key}")
        return json.loads(cached)

    print(f"CACHE MISS: {cache_key}")
    announcement = get_announcement(db, announcement_id)
    if not announcement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Announcement not found"
        )

    response = _build_announcement_response(announcement)
    redis_client.setex(
        cache_key,
        CACHE_TTL,
        json.dumps(response, default=str)
    )
    print(f"CACHE CREATED: {cache_key}")
    return response


@router.post("/", response_model=AnnouncementResponse, status_code=status.HTTP_201_CREATED)
def broadcast_announcement(
    announcement_in: AnnouncementCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "teacher"))
):
    try:
        created = create_announcement(
            db=db,
            announcement_data=announcement_in.model_dump(),
            created_by_uid=current_user.uid
        )
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

    deleted = delete_announcement(db, announcement_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Announcement not found"
        )

    _clear_announcements_cache()
    return {"message": "Announcement deleted successfully"}
