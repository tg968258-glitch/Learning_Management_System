import json

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from Backend.database import get_db
from Backend.src.core.auth_dependency import (
    get_current_user,
    require_roles,
)
from Backend.src.core.course_access import accessible_course_ids, require_course_access
from Backend.src.core.cache import CACHE_TTL, redis_client
from Backend.src.models.course import Course
from Backend.src.models.teacher import Teacher
from Backend.src.models.user import User
from Backend.src.schemas.communication import (
    ClassSessionCreate,
    ClassSessionResponse,
    ClassSessionUpdate,
)
from Backend.src.services.session_service import (
    create_session,
    delete_session,
    get_all_sessions,
    get_session,
    get_sessions_by_course,
    update_session,
)


router = APIRouter(
    prefix="/sessions",
    tags=["Class Sessions"]
)
from Backend.src.services.notification_service import notify_course_students


# =========================================================
# CACHE HELPER
# =========================================================

def _clear_sessions_cache() -> None:
    """
    Delete cached session data after
    create/update/delete operations.
    """

    keys = (
        list(redis_client.scan_iter(match="sessions:*"))
        + list(redis_client.scan_iter(match="session:*"))
    )

    deleted_count = 0

    for key in set(keys):
        redis_client.delete(key)
        deleted_count += 1

    print(
        f"SESSIONS CACHE CLEARED: {deleted_count} key(s)"
    )


# =========================================================
# RESPONSE HELPER
# =========================================================

def _build_session_response(
    db: Session,
    session: object
) -> dict:
    """
    Build frontend-friendly session response
    including course name and teacher name.
    """

    teacher = None

    if session.teacher_id:
        teacher = (
            db.query(Teacher)
            .filter(
                Teacher.teacher_id
                == session.teacher_id
            )
            .first()
        )

    course = (
        db.query(Course)
        .filter(
            Course.course_id
            == session.course_id
        )
        .first()
    )

    return {
        "session_id": session.session_id,
        "course_id": session.course_id,
        "teacher_id": session.teacher_id,
        "session_date": session.session_date,
        "start_time": session.start_time,
        "end_time": session.end_time,
        "topic": session.topic,
        "meeting_link": session.meeting_link,
        "teacher_name": (
            teacher.name
            if teacher
            else None
        ),
        "course_name": (
            course.course_name
            if course
            else None
        ),
    }


# =========================================================
# GET ALL SESSIONS
# =========================================================

@router.get(
    "/",
    response_model=list[ClassSessionResponse]
)
def list_all_sessions(
    course_id: int | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all class sessions.

    Optional:
    /sessions/?course_id=1
    """

    allowed_course_ids = accessible_course_ids(db, current_user)
    if allowed_course_ids is not None:
        sessions = get_all_sessions(db, course_id)
        return [
            _build_session_response(db, session)
            for session in sessions
            if session.course_id in allowed_course_ids
        ]

    cache_key = (
        f"sessions:all:{course_id}"
        if course_id is not None
        else "sessions:all"
    )

    cached = redis_client.get(cache_key)

    if cached:
        print(f"CACHE HIT: {cache_key}")
        return json.loads(cached)

    print(f"CACHE MISS: {cache_key}")

    sessions = get_all_sessions(
        db,
        course_id
    )

    response = [
        _build_session_response(db, session)
        for session in sessions
    ]

    redis_client.setex(
        cache_key,
        CACHE_TTL,
        json.dumps(
            response,
            default=str
        )
    )

    print(f"CACHE CREATED: {cache_key}")

    return response


# =========================================================
# GET SESSIONS BY COURSE
# =========================================================

@router.get(
    "/course/{course_id}",
    response_model=list[ClassSessionResponse]
)
def list_course_sessions(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all sessions belonging to one course.
    """

    if course_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Course ID must be positive"
        )

    require_course_access(db, current_user, course_id)

    cache_key = f"sessions:course:{course_id}"

    cached = redis_client.get(cache_key)

    if cached:
        print(f"CACHE HIT: {cache_key}")
        return json.loads(cached)

    print(f"CACHE MISS: {cache_key}")

    sessions = get_sessions_by_course(
        db,
        course_id
    )

    response = [
        _build_session_response(db, session)
        for session in sessions
    ]

    redis_client.setex(
        cache_key,
        CACHE_TTL,
        json.dumps(
            response,
            default=str
        )
    )

    print(f"CACHE CREATED: {cache_key}")

    return response


# =========================================================
# GET SINGLE SESSION
# =========================================================

@router.get(
    "/{session_id}",
    response_model=ClassSessionResponse
)
def get_single_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get one class session by ID.
    """

    if session_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Session ID must be positive"
        )

    session = get_session(
        db,
        session_id
    )

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )

    require_course_access(db, current_user, session.course_id)

    cache_key = f"session:{session_id}"

    cached = redis_client.get(cache_key)

    if cached:
        print(f"CACHE HIT: {cache_key}")
        return json.loads(cached)

    print(f"CACHE MISS: {cache_key}")

    response = _build_session_response(
        db,
        session
    )

    redis_client.setex(
        cache_key,
        CACHE_TTL,
        json.dumps(
            response,
            default=str
        )
    )

    print(f"CACHE CREATED: {cache_key}")

    return response


# =========================================================
# CREATE SESSION
# =========================================================

@router.post(
    "/",
    response_model=ClassSessionResponse,
    status_code=status.HTTP_201_CREATED
)
def schedule_class_session(
    session_in: ClassSessionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles("admin", "teacher")
    )
):
    """
    Create/schedule a new class session.
    """

    try:
        require_course_access(db, current_user, session_in.course_id)
        created = create_session(
            db,
            session_in.model_dump()
        )

        notify_course_students(
            db, created.course_id, "class_session", "New class session",
            f"{created.topic or 'A class session'} is scheduled for {created.session_date}.",
            session_id=created.session_id,
        )

        _clear_sessions_cache()

        return _build_session_response(
            db,
            created
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        ) from e


# =========================================================
# UPDATE SESSION
# =========================================================

@router.put(
    "/{session_id}",
    response_model=ClassSessionResponse
)
def update_class_session(
    session_id: int,
    session_in: ClassSessionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles("admin", "teacher")
    )
):
    """
    Update an existing class session.
    """

    if session_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Session ID must be positive"
        )

    existing = get_session(db, session_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Session not found")
    require_course_access(db, current_user, existing.course_id)

    try:
        updated = update_session(
            db,
            session_id,
            session_in.model_dump(
                exclude_unset=True
            )
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        ) from e

    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )

    _clear_sessions_cache()

    return _build_session_response(
        db,
        updated
    )


# =========================================================
# DELETE SESSION
# =========================================================

@router.delete(
    "/{session_id}"
)
def remove_class_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles("admin", "teacher")
    )
):
    """
    Delete a class session.
    """

    if session_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Session ID must be positive"
        )

    existing = get_session(db, session_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Session not found")
    require_course_access(db, current_user, existing.course_id)

    deleted = delete_session(
        db,
        session_id
    )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )

    _clear_sessions_cache()

    return {
        "message": "Session deleted successfully"
    }
