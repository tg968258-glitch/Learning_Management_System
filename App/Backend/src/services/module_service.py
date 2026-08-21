from sqlalchemy.orm import Session

from Backend.src.models.course import Course
from Backend.src.models.module import Module
from Backend.src.utils.logger import logger


def get_modules_by_course(
    db: Session,
    course_id: int,
    published_only: bool = False
) -> list[Module]:
    query = db.query(Module).filter(Module.course_id == course_id)
    if published_only:
        query = query.filter(Module.is_published.is_(True))
    return query.all()


def get_module(db: Session, module_id: int) -> Module | None:
    return db.query(Module).filter(Module.module_id == module_id).first()


def create_module(
    db: Session,
    module_data: dict,
    published_by_uid: str | None = None
) -> Module:
    course = db.query(Course).filter(Course.course_id == module_data["course_id"]).first()
    if not course:
        raise ValueError("Course does not exist")

    module = Module(
        course_id=module_data["course_id"],
        module_name=module_data["module_name"],
        description=module_data.get("description"),
        is_published=module_data.get("is_published", False),
        published_by=published_by_uid if module_data.get("is_published") else None
    )

    try:
        db.add(module)
        db.commit()
        db.refresh(module)
        logger.info(f"Module created: {module.module_id} for course {module.course_id}")
        return module
    except Exception:
        db.rollback()
        raise


def update_module(
    db: Session,
    module_id: int,
    updated_data: dict,
    editor_uid: str | None = None
) -> Module | None:
    module = get_module(db, module_id)
    if not module:
        return None

    for field, value in updated_data.items():
        if value is not None and hasattr(module, field):
            setattr(module, field, value)

    if updated_data.get("is_published") and not module.published_by:
        module.published_by = editor_uid

    try:
        db.commit()
        db.refresh(module)
        logger.info(f"Module updated: {module_id}")
        return module
    except Exception:
        db.rollback()
        raise


def delete_module(db: Session, module_id: int) -> Module | None:
    module = get_module(db, module_id)
    if not module:
        return None

    try:
        db.delete(module)
        db.commit()
        logger.info(f"Module deleted: {module_id}")
        return module
    except Exception:
        db.rollback()
        raise
