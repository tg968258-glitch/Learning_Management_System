from datetime import datetime

from sqlalchemy.orm import Session

from Backend.src.models.lesson import Lesson, LessonContent, Resource
from Backend.src.models.module import Module
from Backend.src.utils.logger import logger

# =========================================================
# LESSON CRUD
# =========================================================

def get_lessons_by_module(
    db: Session,
    module_id: int,
    published_only: bool = False
) -> list[Lesson]:
    query = db.query(Lesson).filter(Lesson.module_id == module_id)
    if published_only:
        query = query.filter(Lesson.is_published.is_(True))
    return query.all()


def get_lesson(db: Session, lesson_id: int) -> Lesson | None:
    return db.query(Lesson).filter(Lesson.lesson_id == lesson_id).first()


def create_lesson(db: Session, lesson_data: dict) -> Lesson:
    module = db.query(Module).filter(Module.module_id == lesson_data["module_id"]).first()
    if not module:
        raise ValueError("Module does not exist")

    lesson = Lesson(
        module_id=lesson_data["module_id"],
        lesson_title=lesson_data["lesson_title"],
        is_published=lesson_data.get("is_published", False),
        created_at=datetime.utcnow()
    )

    try:
        db.add(lesson)
        db.commit()
        db.refresh(lesson)
        logger.info(f"Lesson created: {lesson.lesson_id} for module {lesson.module_id}")
        return lesson
    except Exception:
        db.rollback()
        raise


def update_lesson(
    db: Session,
    lesson_id: int,
    updated_data: dict
) -> Lesson | None:
    lesson = get_lesson(db, lesson_id)
    if not lesson:
        return None

    for field, value in updated_data.items():
        if value is not None and hasattr(lesson, field):
            setattr(lesson, field, value)

    lesson.updated_at = datetime.utcnow()

    try:
        db.commit()
        db.refresh(lesson)
        logger.info(f"Lesson updated: {lesson_id}")
        return lesson
    except Exception:
        db.rollback()
        raise


def delete_lesson(db: Session, lesson_id: int) -> Lesson | None:
    lesson = get_lesson(db, lesson_id)
    if not lesson:
        return None

    try:
        # Delete related contents and resources first
        db.query(LessonContent).filter(LessonContent.lesson_id == lesson_id).delete()
        db.query(Resource).filter(Resource.lesson_id == lesson_id).delete()
        db.delete(lesson)
        db.commit()
        logger.info(f"Lesson deleted: {lesson_id}")
        return lesson
    except Exception:
        db.rollback()
        raise


# =========================================================
# LESSON CONTENTS
# =========================================================

def get_contents_by_lesson(db: Session, lesson_id: int) -> list[LessonContent]:
    return (
        db.query(LessonContent)
        .filter(LessonContent.lesson_id == lesson_id)
        .order_by(LessonContent.sequence_number.asc())
        .all()
    )


def add_lesson_content(db: Session, content_data: dict) -> LessonContent:
    lesson = get_lesson(db, content_data["lesson_id"])
    if not lesson:
        raise ValueError("Lesson does not exist")

    content = LessonContent(
        lesson_id=content_data["lesson_id"],
        content_type=content_data["content_type"],
        content=content_data["content"],
        sequence_number=content_data.get("sequence_number", 1),
        created_at=datetime.utcnow()
    )

    try:
        db.add(content)
        db.commit()
        db.refresh(content)
        return content
    except Exception:
        db.rollback()
        raise


def update_lesson_content(
    db: Session,
    content_id: int,
    updated_data: dict
) -> LessonContent | None:
    content = db.query(LessonContent).filter(LessonContent.content_id == content_id).first()
    if not content:
        return None

    for field, value in updated_data.items():
        if value is not None and hasattr(content, field):
            setattr(content, field, value)

    content.updated_at = datetime.utcnow()

    try:
        db.commit()
        db.refresh(content)
        return content
    except Exception:
        db.rollback()
        raise


def delete_lesson_content(db: Session, content_id: int) -> bool:
    content = db.query(LessonContent).filter(LessonContent.content_id == content_id).first()
    if not content:
        return False

    try:
        db.delete(content)
        db.commit()
        return True
    except Exception:
        db.rollback()
        raise


# =========================================================
# RESOURCES
# =========================================================

def get_resources_by_lesson(db: Session, lesson_id: int) -> list[Resource]:
    return db.query(Resource).filter(Resource.lesson_id == lesson_id).all()


def add_resource(db: Session, resource_data: dict) -> Resource:
    lesson = get_lesson(db, resource_data["lesson_id"])
    if not lesson:
        raise ValueError("Lesson does not exist")

    resource = Resource(
        lesson_id=resource_data["lesson_id"],
        resource_name=resource_data["resource_name"],
        resource_type=resource_data.get("resource_type"),
        resource_url=resource_data["resource_url"],
        created_at=datetime.utcnow()
    )

    try:
        db.add(resource)
        db.commit()
        db.refresh(resource)
        return resource
    except Exception:
        db.rollback()
        raise


def update_resource(
    db: Session,
    resource_id: int,
    updated_data: dict
) -> Resource | None:
    resource = db.query(Resource).filter(Resource.resource_id == resource_id).first()
    if not resource:
        return None

    for field, value in updated_data.items():
        if value is not None and hasattr(resource, field):
            setattr(resource, field, value)

    resource.updated_at = datetime.utcnow()

    try:
        db.commit()
        db.refresh(resource)
        return resource
    except Exception:
        db.rollback()
        raise


def delete_resource(db: Session, resource_id: int) -> bool:
    resource = db.query(Resource).filter(Resource.resource_id == resource_id).first()
    if not resource:
        return False

    try:
        db.delete(resource)
        db.commit()
        return True
    except Exception:
        db.rollback()
        raise
