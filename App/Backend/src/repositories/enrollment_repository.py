from datetime import datetime
from sqlalchemy.orm import Session

from Backend.src.models.enrollment import Enrollment


class EnrollmentRepository:
    @staticmethod
    def get_by_id(db: Session, enrollment_id: int) -> Enrollment | None:
        return db.query(Enrollment).filter(Enrollment.enrollment_id == enrollment_id).first()

    @staticmethod
    def get_by_student_and_course(db: Session, student_id: int, course_id: int) -> Enrollment | None:
        return (
            db.query(Enrollment)
            .filter(
                Enrollment.student_id == student_id,
                Enrollment.course_id == course_id
            )
            .first()
        )

    @staticmethod
    def get_by_student(db: Session, student_id: int, status: str | None = None) -> list[Enrollment]:
        query = db.query(Enrollment).filter(Enrollment.student_id == student_id)
        if status:
            query = query.filter(Enrollment.status == status)
        return query.all()

    @staticmethod
    def get_by_course(db: Session, course_id: int, status: str | None = None) -> list[Enrollment]:
        query = db.query(Enrollment).filter(Enrollment.course_id == course_id)
        if status:
            query = query.filter(Enrollment.status == status)
        return query.all()

    @staticmethod
    def count(db: Session, status: str | None = None) -> int:
        query = db.query(Enrollment)
        if status:
            query = query.filter(Enrollment.status == status)
        return query.count()

    @staticmethod
    def create(db: Session, student_id: int, course_id: int, status: str = "active") -> Enrollment:
        enrollment = Enrollment(
            student_id=student_id,
            course_id=course_id,
            status=status,
            enrollment_date=datetime.utcnow()
        )
        db.add(enrollment)
        db.commit()
        db.refresh(enrollment)
        return enrollment

    @staticmethod
    def update_status(db: Session, enrollment: Enrollment, status: str) -> Enrollment:
        enrollment.status = status
        db.commit()
        db.refresh(enrollment)
        return enrollment
