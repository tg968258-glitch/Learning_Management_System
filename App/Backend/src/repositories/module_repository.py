from sqlalchemy.orm import Session

from Backend.src.models.module import Module


class ModuleRepository:
    @staticmethod
    def get_by_id(db: Session, module_id: int) -> Module | None:
        return db.query(Module).filter(Module.module_id == module_id).first()

    @staticmethod
    def get_by_course(db: Session, course_id: int) -> list[Module]:
        return (
            db.query(Module)
            .filter(Module.course_id == course_id)
            .all()
        )

    @staticmethod
    def create(db: Session, module_data: dict) -> Module:
        module = Module(
            course_id=module_data["course_id"],
            module_name=module_data["module_name"],
            description=module_data.get("description"),
            is_published=module_data.get("is_published", False),
            published_by=module_data.get("published_by")
        )
        db.add(module)
        db.commit()
        db.refresh(module)
        return module

    @staticmethod
    def update(db: Session, module: Module, update_data: dict) -> Module:
        for field, value in update_data.items():
            if hasattr(module, field) and value is not None:
                setattr(module, field, value)
        db.commit()
        db.refresh(module)
        return module

    @staticmethod
    def delete(db: Session, module: Module) -> None:
        db.delete(module)
        db.commit()
