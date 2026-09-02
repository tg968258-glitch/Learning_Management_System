import json

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from sqlalchemy.orm import Session

from Backend.database import get_db
from Backend.src.core.auth_dependency import get_current_user, require_roles
from Backend.src.core.cache import CACHE_TTL, redis_client
from Backend.src.models.user import User
from Backend.src.utils.file_upload import save_uploaded_file
from Backend.src.schemas.lessons import (
    LessonContentCreate,
    LessonContentResponse,
    LessonContentUpdate,
    LessonCreate,
    LessonDetailResponse,
    LessonResponse,
    LessonUpdate,
    ResourceCreate,
    ResourceResponse,
    ResourceUpdate,
)
from Backend.src.services.lesson_service import (
    add_lesson_content,
    add_resource,
    create_lesson,
    delete_lesson,
    delete_lesson_content,
    delete_resource,
    get_contents_by_lesson,
    get_lesson,
    get_lessons_by_module,
    get_resources_by_lesson,
    update_lesson,
    update_lesson_content,
    update_resource,
)

router = APIRouter(
    prefix="/lessons",
    tags=["Lessons"]
)


# =========================================================
# CACHE HELPER
# =========================================================

def _clear_lessons_cache():
    """Delete all cached lesson results and details."""
    keys = list(redis_client.scan_iter(match="lessons:*")) + list(redis_client.scan_iter(match="lesson:*"))
    deleted_count = 0
    for key in set(keys):
        redis_client.delete(key)
        deleted_count += 1
    print(f"LESSONS CACHE CLEARED: {deleted_count} key(s)")


def _build_lesson_response(l) -> dict:
    return {
        "lesson_id": l.lesson_id,
        "module_id": l.module_id,
        "lesson_title": l.lesson_title,
        "is_published": l.is_published,
        "created_at": l.created_at,
        "updated_at": l.updated_at,
    }


def _build_content_response(c) -> dict:
    return {
        "content_id": c.content_id,
        "lesson_id": c.lesson_id,
        "content_type": c.content_type,
        "content": c.content,
        "sequence_number": c.sequence_number,
        "created_at": c.created_at,
        "updated_at": c.updated_at,
    }


def _build_resource_response(r) -> dict:
    return {
        "resource_id": r.resource_id,
        "lesson_id": r.lesson_id,
        "resource_name": r.resource_name,
        "resource_type": r.resource_type,
        "resource_url": r.resource_url,
        "created_at": r.created_at,
    }


# =========================================================
# LESSON ROUTES
# =========================================================

@router.get("/module/{module_id}", response_model=list[LessonResponse])
def list_module_lessons(
    module_id: int,
    published_only: bool = Query(False, description="Filter only published lessons"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if module_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Module ID must be positive"
        )
    if current_user.role == "student":
        published_only = True

    cache_key = f"lessons:module:{module_id}:{published_only}"

    cached = redis_client.get(cache_key)
    if cached:
        print(f"CACHE HIT: {cache_key}")
        return json.loads(cached)

    print(f"CACHE MISS: {cache_key}")
    lessons = get_lessons_by_module(db, module_id, published_only=published_only)
    response = [_build_lesson_response(l) for l in lessons]

    redis_client.setex(
        cache_key,
        CACHE_TTL,
        json.dumps(response, default=str)
    )
    print(f"CACHE CREATED: {cache_key}")
    return response


@router.get("/{lesson_id}", response_model=LessonDetailResponse)
def get_single_lesson_details(
    lesson_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if lesson_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Lesson ID must be positive"
        )

    cache_key = f"lesson:{lesson_id}"

    cached = redis_client.get(cache_key)
    if cached:
        print(f"CACHE HIT: {cache_key}")
        lesson_dict = json.loads(cached)
        if current_user.role == "student" and not lesson_dict.get("is_published"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Lesson is not published yet"
            )
        return lesson_dict

    print(f"CACHE MISS: {cache_key}")
    lesson = get_lesson(db, lesson_id)
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson not found"
        )

    if current_user.role == "student" and not lesson.is_published:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Lesson is not published yet"
        )

    contents = get_contents_by_lesson(db, lesson_id)
    resources = get_resources_by_lesson(db, lesson_id)

    response = {
        "lesson_id": lesson.lesson_id,
        "module_id": lesson.module_id,
        "lesson_title": lesson.lesson_title,
        "is_published": lesson.is_published,
        "created_at": lesson.created_at,
        "updated_at": lesson.updated_at,
        "contents": [_build_content_response(c) for c in contents],
        "resources": [_build_resource_response(r) for r in resources]
    }

    redis_client.setex(
        cache_key,
        CACHE_TTL,
        json.dumps(response, default=str)
    )
    print(f"CACHE CREATED: {cache_key}")
    return response


@router.post("/", response_model=LessonResponse, status_code=status.HTTP_201_CREATED)
def add_new_lesson(
    lesson_in: LessonCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "teacher"))
):
    try:
        created = create_lesson(db, lesson_in.model_dump())
        _clear_lessons_cache()
        return _build_lesson_response(created)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        ) from e


@router.put("/{lesson_id}", response_model=LessonResponse)
def update_existing_lesson(
    lesson_id: int,
    lesson_in: LessonUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "teacher"))
):
    if lesson_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Lesson ID must be positive"
        )

    updated = update_lesson(db, lesson_id, lesson_in.model_dump(exclude_unset=True))
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson not found"
        )

    _clear_lessons_cache()
    return _build_lesson_response(updated)


@router.delete("/{lesson_id}")
def remove_lesson(
    lesson_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "teacher"))
):
    if lesson_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Lesson ID must be positive"
        )

    deleted = delete_lesson(db, lesson_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson not found"
        )

    _clear_lessons_cache()
    return {"message": "Lesson deleted successfully"}


# =========================================================
# LESSON CONTENTS
# =========================================================

@router.post("/contents/", response_model=LessonContentResponse, status_code=status.HTTP_201_CREATED)
def add_content_to_lesson(
    content_in: LessonContentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "teacher"))
):
    try:
        created = add_lesson_content(db, content_in.model_dump())
        _clear_lessons_cache()
        return _build_content_response(created)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        ) from e


@router.put("/contents/{content_id}", response_model=LessonContentResponse)
def update_content(
    content_id: int,
    content_in: LessonContentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "teacher"))
):
    updated = update_lesson_content(db, content_id, content_in.model_dump(exclude_unset=True))
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson content not found"
        )
    _clear_lessons_cache()
    return _build_content_response(updated)


@router.delete("/contents/{content_id}")
def remove_content(
    content_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "teacher"))
):
    if not delete_lesson_content(db, content_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson content not found"
        )
    _clear_lessons_cache()
    return {"message": "Lesson content deleted successfully"}


# =========================================================
# RESOURCES
# =========================================================

@router.post("/resources/", response_model=ResourceResponse, status_code=status.HTTP_201_CREATED)
def add_resource_to_lesson(
    resource_in: ResourceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "teacher"))
):
    try:
        created = add_resource(db, resource_in.model_dump())
        _clear_lessons_cache()
        return _build_resource_response(created)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        ) from e


@router.post("/{lesson_id}/resources/upload-pdf", response_model=ResourceResponse, status_code=status.HTTP_201_CREATED)
async def upload_lesson_pdf_resource(
    lesson_id: int,
    resource_name: str = Form(..., description="Display title for the resource"),
    resource_type: str = Form("pdf", description="Resource type (e.g. pdf, notes, slides)"),
    file: UploadFile = File(..., description="PDF document or presentation"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "teacher"))
):
    file_url = await save_uploaded_file(file, subfolder="resources")
    try:
        created = add_resource(db, {
            "lesson_id": lesson_id,
            "resource_name": resource_name,
            "resource_type": resource_type,
            "resource_url": file_url
        })
        _clear_lessons_cache()
        return _build_resource_response(created)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        ) from e


@router.put("/resources/{resource_id}", response_model=ResourceResponse)
def update_existing_resource(
    resource_id: int,
    resource_in: ResourceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "teacher"))
):
    updated = update_resource(db, resource_id, resource_in.model_dump(exclude_unset=True))
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found"
        )
    _clear_lessons_cache()
    return _build_resource_response(updated)


@router.delete("/resources/{resource_id}")
def remove_resource(
    resource_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "teacher"))
):
    if not delete_resource(db, resource_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found"
        )
    _clear_lessons_cache()
    return {"message": "Resource deleted successfully"}
