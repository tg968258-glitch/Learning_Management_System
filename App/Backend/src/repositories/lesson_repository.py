from datetime import datetime
from sqlalchemy.orm import Session

from Backend.src.models.lesson import Lesson, LessonContent, Resource


class LessonRepository:
    # --- Lesson CRUD ---
    @staticmethod
    def get_by_id(db: Session, lesson_id: int) -> Lesson | None:
        return db.query(Lesson).filter(Lesson.lesson_id == lesson_id).first()

    @staticmethod
    def get_by_module(
        db: Session,
        module_id: int,
        published_only: bool = False
    ) -> list[Lesson]:
        query = db.query(Lesson).filter(Lesson.module_id == module_id)
        if published_only:
            query = query.filter(Lesson.is_published.is_(True))
        return query.all()

    @staticmethod
    def create_lesson(db: Session, lesson_data: dict) -> Lesson:
        lesson = Lesson(
            module_id=lesson_data["module_id"],
            lesson_title=lesson_data["lesson_title"],
            is_published=lesson_data.get("is_published", False),
            created_at=datetime.utcnow()
        )
        db.add(lesson)
        db.commit()
        db.refresh(lesson)
        return lesson

    @staticmethod
    def update_lesson(db: Session, lesson: Lesson, update_data: dict) -> Lesson:
        for field, value in update_data.items():
            if hasattr(lesson, field) and value is not None:
                setattr(lesson, field, value)
        lesson.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(lesson)
        return lesson

    @staticmethod
    def delete_lesson(db: Session, lesson: Lesson) -> None:
        # Delete related contents and resources
        db.query(LessonContent).filter(LessonContent.lesson_id == lesson.lesson_id).delete()
        db.query(Resource).filter(Resource.lesson_id == lesson.lesson_id).delete()
        db.delete(lesson)
        db.commit()

    # --- Lesson Contents ---
    @staticmethod
    def get_contents_by_lesson(db: Session, lesson_id: int) -> list[LessonContent]:
        return (
            db.query(LessonContent)
            .filter(LessonContent.lesson_id == lesson_id)
            .order_by(LessonContent.sequence_number.asc())
            .all()
        )

    @staticmethod
    def get_content_by_id(db: Session, content_id: int) -> LessonContent | None:
        return db.query(LessonContent).filter(LessonContent.content_id == content_id).first()

    @staticmethod
    def create_content(db: Session, content_data: dict) -> LessonContent:
        content = LessonContent(
            lesson_id=content_data["lesson_id"],
            content_type=content_data["content_type"],
            content=content_data["content"],
            sequence_number=content_data.get("sequence_number", 1),
            created_at=datetime.utcnow()
        )
        db.add(content)
        db.commit()
        db.refresh(content)
        return content

    @staticmethod
    def update_content(db: Session, content: LessonContent, update_data: dict) -> LessonContent:
        for field, value in update_data.items():
            if hasattr(content, field) and value is not None:
                setattr(content, field, value)
        content.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(content)
        return content

    @staticmethod
    def delete_content(db: Session, content: LessonContent) -> None:
        db.delete(content)
        db.commit()

    # --- Resources ---
    @staticmethod
    def get_resources_by_lesson(db: Session, lesson_id: int) -> list[Resource]:
        return db.query(Resource).filter(Resource.lesson_id == lesson_id).all()

    @staticmethod
    def get_resource_by_id(db: Session, resource_id: int) -> Resource | None:
        return db.query(Resource).filter(Resource.resource_id == resource_id).first()

    @staticmethod
    def create_resource(db: Session, resource_data: dict) -> Resource:
        resource = Resource(
            lesson_id=resource_data["lesson_id"],
            resource_name=resource_data["resource_name"],
            resource_type=resource_data.get("resource_type"),
            resource_url=resource_data["resource_url"],
            created_at=datetime.utcnow()
        )
        db.add(resource)
        db.commit()
        db.refresh(resource)
        return resource

    @staticmethod
    def update_resource(db: Session, resource: Resource, update_data: dict) -> Resource:
        for field, value in update_data.items():
            if hasattr(resource, field) and value is not None:
                setattr(resource, field, value)
        resource.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(resource)
        return resource

    @staticmethod
    def delete_resource(db: Session, resource: Resource) -> None:
        db.delete(resource)
        db.commit()
