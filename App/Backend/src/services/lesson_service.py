from sqlalchemy.orm import Session

from Backend.src.models.lesson import Lesson, LessonContent, Resource
from Backend.src.repositories.lesson_repository import LessonRepository
from Backend.src.repositories.module_repository import ModuleRepository
from Backend.src.utils.logger import logger

# =========================================================
# LESSON CRUD
# =========================================================

def get_lessons_by_module(
    db: Session,
    module_id: int,
    published_only: bool = False
) -> list[Lesson]:
    return LessonRepository.get_by_module(db, module_id=module_id, published_only=published_only)


def get_lesson(db: Session, lesson_id: int) -> Lesson | None:
    return LessonRepository.get_by_id(db, lesson_id)


def create_lesson(db: Session, lesson_data: dict) -> Lesson:
    module = ModuleRepository.get_by_id(db, lesson_data["module_id"])
    if not module:
        raise ValueError("Module does not exist")

    lesson = LessonRepository.create_lesson(db, lesson_data)
    logger.info(f"Lesson created: {lesson.lesson_id} for module {lesson.module_id}")
    return lesson


def update_lesson(
    db: Session,
    lesson_id: int,
    updated_data: dict
) -> Lesson | None:
    lesson = LessonRepository.get_by_id(db, lesson_id)
    if not lesson:
        return None

    updated = LessonRepository.update_lesson(db, lesson, updated_data)
    logger.info(f"Lesson updated: {lesson_id}")
    return updated


def delete_lesson(db: Session, lesson_id: int) -> Lesson | None:
    lesson = LessonRepository.get_by_id(db, lesson_id)
    if not lesson:
        return None

    LessonRepository.delete_lesson(db, lesson)
    logger.info(f"Lesson deleted: {lesson_id}")
    return lesson


# =========================================================
# LESSON CONTENTS
# =========================================================

def get_contents_by_lesson(db: Session, lesson_id: int) -> list[LessonContent]:
    return LessonRepository.get_contents_by_lesson(db, lesson_id)


def add_lesson_content(db: Session, content_data: dict) -> LessonContent:
    lesson = LessonRepository.get_by_id(db, content_data["lesson_id"])
    if not lesson:
        raise ValueError("Lesson does not exist")

    return LessonRepository.create_content(db, content_data)


def update_lesson_content(
    db: Session,
    content_id: int,
    updated_data: dict
) -> LessonContent | None:
    content = LessonRepository.get_content_by_id(db, content_id)
    if not content:
        return None

    return LessonRepository.update_content(db, content, updated_data)


def delete_lesson_content(db: Session, content_id: int) -> bool:
    content = LessonRepository.get_content_by_id(db, content_id)
    if not content:
        return False

    LessonRepository.delete_content(db, content)
    return True


# =========================================================
# RESOURCES
# =========================================================

def get_resources_by_lesson(db: Session, lesson_id: int) -> list[Resource]:
    return LessonRepository.get_resources_by_lesson(db, lesson_id)


def add_resource(db: Session, resource_data: dict) -> Resource:
    lesson = LessonRepository.get_by_id(db, resource_data["lesson_id"])
    if not lesson:
        raise ValueError("Lesson does not exist")

    return LessonRepository.create_resource(db, resource_data)


def update_resource(
    db: Session,
    resource_id: int,
    updated_data: dict
) -> Resource | None:
    resource = LessonRepository.get_resource_by_id(db, resource_id)
    if not resource:
        return None

    return LessonRepository.update_resource(db, resource, updated_data)


def delete_resource(db: Session, resource_id: int) -> bool:
    resource = LessonRepository.get_resource_by_id(db, resource_id)
    if not resource:
        return False

    LessonRepository.delete_resource(db, resource)
    return True
