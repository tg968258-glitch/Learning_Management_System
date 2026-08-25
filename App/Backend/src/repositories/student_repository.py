from sqlalchemy.orm import Session

from Backend.src.models.student import Student


class StudentRepository:
    @staticmethod
    def get_by_id(db: Session, student_id: int) -> Student | None:
        return db.query(Student).filter(Student.student_id == student_id).first()

    @staticmethod
    def get_by_uid(db: Session, uid: str) -> Student | None:
        return db.query(Student).filter(Student.uid == uid).first()

    @staticmethod
    def get_all(db: Session) -> list[Student]:
        return db.query(Student).all()

    @staticmethod
    def count(db: Session) -> int:
        return db.query(Student).count()

    @staticmethod
    def create(db: Session, student_data: dict) -> Student:
        student = Student(
            uid=student_data["uid"],
            name=student_data["name"],
            date_of_birth=student_data.get("date_of_birth"),
            gender=student_data.get("gender"),
            phone_number=student_data.get("phone_number")
        )
        db.add(student)
        db.commit()
        db.refresh(student)
        return student

    @staticmethod
    def update(db: Session, student: Student, update_data: dict) -> Student:
        for field, value in update_data.items():
            if hasattr(student, field) and value is not None:
                setattr(student, field, value)
        db.commit()
        db.refresh(student)
        return student

    @staticmethod
    def delete(db: Session, student: Student) -> None:
        db.delete(student)
        db.commit()
