from sqlalchemy.orm import Session

from Backend.src.models.student import Student
from Backend.src.repositories.student_repository import StudentRepository


def get_all_students(db: Session) -> list[Student]:
    return StudentRepository.get_all(db)


def get_student(db: Session, student_id: int) -> Student | None:
    return StudentRepository.get_by_id(db, student_id)


def get_student_by_uid(db: Session, uid: str) -> Student:
    student = StudentRepository.get_by_uid(db, uid)
    if not student:
        raise ValueError("Student profile not found")
    return student


def update_student(
    db: Session,
    student_id: int,
    updated_data: dict
) -> Student | None:
    student = StudentRepository.get_by_id(db, student_id)
    if not student:
        return None

    return StudentRepository.update(db, student, updated_data)


def delete_student(
    db: Session,
    student_id: int
) -> Student | None:
    student = StudentRepository.get_by_id(db, student_id)
    if not student:
        return None

    StudentRepository.delete(db, student)
    return student