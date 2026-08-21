from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from Backend.database import get_db
from Backend.src.core.auth_dependency import get_current_user, require_roles
from Backend.src.models.user import User
from Backend.src.schemas.modules import ModuleCreate, ModuleResponse, ModuleUpdate
from Backend.src.services.module_service import (
    create_module,
    delete_module,
    get_module,
    get_modules_by_course,
    update_module,
)

router = APIRouter(
    prefix="/modules",
    tags=["Modules"]
)


@router.get("/course/{course_id}", response_model=list[ModuleResponse])
def list_course_modules(
    course_id: int,
    published_only: bool = Query(False, description="Filter only published modules"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if course_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Course ID must be positive"
        )
    # Students should only see published modules
    if current_user.role == "student":
        published_only = True

    return get_modules_by_course(db, course_id, published_only=published_only)


@router.get("/{module_id}", response_model=ModuleResponse)
def get_single_module(
    module_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if module_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Module ID must be positive"
        )

    module = get_module(db, module_id)
    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module not found"
        )

    if current_user.role == "student" and not module.is_published:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Module is not published yet"
        )

    return module


@router.post("/", response_model=ModuleResponse, status_code=status.HTTP_201_CREATED)
def add_new_module(
    module_in: ModuleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "teacher"))
):
    try:
        return create_module(
            db=db,
            module_data=module_in.model_dump(),
            published_by_uid=current_user.uid
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        ) from e


@router.put("/{module_id}", response_model=ModuleResponse)
def update_existing_module(
    module_id: int,
    module_in: ModuleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "teacher"))
):
    if module_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Module ID must be positive"
        )

    updated = update_module(
        db=db,
        module_id=module_id,
        updated_data=module_in.model_dump(exclude_unset=True),
        editor_uid=current_user.uid
    )

    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module not found"
        )

    return updated


@router.delete("/{module_id}")
def remove_module(
    module_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "teacher"))
):
    if module_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Module ID must be positive"
        )

    deleted = delete_module(db, module_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module not found"
        )

    return {"message": "Module deleted successfully"}
