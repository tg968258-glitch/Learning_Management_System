from datetime import date
from sqlalchemy import func
from sqlalchemy.orm import Session

from Backend.src.models.assignment import Assignment
from Backend.src.models.class_session import ClassSession
from Backend.src.models.course import Course
from Backend.src.models.enrollment import Enrollment
from Backend.src.models.progress import LessonProgress
from Backend.src.models.student import Student


class StudentRepository:
    @staticmethod
    def get_dashboard_stats(db: Session, uid: str) -> dict:
        """Aggregate dashboard counts for the student identified by the auth UID."""
        row = db.query(
            db.query(func.count(func.distinct(Enrollment.course_id)))
            .join(Student, Student.student_id == Enrollment.student_id)
            .join(Course, Course.course_id == Enrollment.course_id)
            .filter(Student.uid == uid, Enrollment.status == "active", Course.status == "active")
            .scalar_subquery()
            .label("enrolled_courses"),
            db.query(func.count(LessonProgress.lesson_id))
            .join(Student, Student.student_id == LessonProgress.student_id)
            .filter(Student.uid == uid, LessonProgress.completed.is_(True))
            .scalar_subquery()
            .label("completed_lessons"),
            db.query(func.count(func.distinct(Assignment.assignment_id)))
            .join(Enrollment, Enrollment.course_id == Assignment.course_id)
            .join(Student, Student.student_id == Enrollment.student_id)
            .join(Course, Course.course_id == Enrollment.course_id)
            .filter(Student.uid == uid, Enrollment.status == "active", Course.status == "active")
            .scalar_subquery()
            .label("assignments"),
            db.query(func.count(func.distinct(ClassSession.session_id)))
            .join(Enrollment, Enrollment.course_id == ClassSession.course_id)
            .join(Student, Student.student_id == Enrollment.student_id)
            .join(Course, Course.course_id == Enrollment.course_id)
            .filter(
                Student.uid == uid,
                Enrollment.status == "active",
                Course.status == "active",
                ClassSession.session_date >= date.today(),
            )
            .scalar_subquery()
            .label("upcoming_sessions"),
        ).one()
        return {key: int(value or 0) for key, value in row._mapping.items()}

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
