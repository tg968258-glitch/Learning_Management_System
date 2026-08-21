from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from Backend.database import get_db
from Backend.src.core.auth_dependency import get_current_user, require_roles
from Backend.src.models.user import User
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

    return get_lessons_by_module(db, module_id, published_only=published_only)


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

    return {
        "lesson_id": lesson.lesson_id,
        "module_id": lesson.module_id,
        "lesson_title": lesson.lesson_title,
        "is_published": lesson.is_published,
        "created_at": lesson.created_at,
        "updated_at": lesson.updated_at,
        "contents": contents,
        "resources": resources
    }


@router.post("/", response_model=LessonResponse, status_code=status.HTTP_201_CREATED)
def add_new_lesson(
    lesson_in: LessonCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "teacher"))
):
    try:
        return create_lesson(db, lesson_in.model_dump())
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

    return updated


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
        return add_lesson_content(db, content_in.model_dump())
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
    return updated


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
        return add_resource(db, resource_in.model_dump())
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
    return updated


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
    return {"message": "Resource deleted successfully"}
