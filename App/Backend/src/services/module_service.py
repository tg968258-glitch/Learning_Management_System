from sqlalchemy.orm import Session

from Backend.src.models.module import Module
from Backend.src.repositories.course_repository import CourseRepository
from Backend.src.repositories.module_repository import ModuleRepository
from Backend.src.utils.logger import logger


def get_modules_by_course(
    db: Session,
    course_id: int,
    published_only: bool = False
) -> list[Module]:
    modules = ModuleRepository.get_by_course(db, course_id)
    if published_only:
        modules = [m for m in modules if m.is_published]
    return modules


def get_module(db: Session, module_id: int) -> Module | None:
    return ModuleRepository.get_by_id(db, module_id)


def create_module(
    db: Session,
    module_data: dict,
    published_by_uid: str | None = None
) -> Module:
    course = CourseRepository.get_by_id(db, module_data["course_id"])
    if not course:
        raise ValueError("Course does not exist")

    is_published = module_data.get("is_published", False)
    data = {
        "course_id": module_data["course_id"],
        "module_name": module_data["module_name"],
        "description": module_data.get("description"),
        "is_published": is_published,
        "published_by": published_by_uid if is_published else None
    }
    module = ModuleRepository.create(db, data)
    logger.info(f"Module created: {module.module_id} for course {module.course_id}")
    return module


def update_module(
    db: Session,
    module_id: int,
    updated_data: dict,
    editor_uid: str | None = None
) -> Module | None:
    module = ModuleRepository.get_by_id(db, module_id)
    if not module:
        return None

    if updated_data.get("is_published") and not module.published_by:
        updated_data["published_by"] = editor_uid

    updated = ModuleRepository.update(db, module, updated_data)
    logger.info(f"Module updated: {module_id}")
    return updated


def delete_module(db: Session, module_id: int) -> Module | None:
    module = ModuleRepository.get_by_id(db, module_id)
    if not module:
        return None

    ModuleRepository.delete(db, module)
    logger.info(f"Module deleted: {module_id}")
    return module
