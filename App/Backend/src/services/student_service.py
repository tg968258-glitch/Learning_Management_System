from sqlalchemy.orm import Session

from Backend.src.models.student import Student
from Backend.src.models.user import User


def get_all_students(db: Session):
    return db.query(Student).all()


def get_student(
    db: Session,
    student_id: int
):
    return (
        db.query(Student)
        .filter(Student.student_id == student_id)
        .first()
    )


def create_student(
    db: Session,
    student_data: dict
):
    uid = student_data["uid"]

    user = (
        db.query(User)
        .filter(User.uid == uid)
        .first()
    )

    if not user:
        raise ValueError(
            "User with this UID does not exist"
        )

    if user.role != "student":
        raise ValueError(
            "This user does not have student role"
        )

    if not user.is_active:
        raise ValueError(
            "Cannot create profile for a deactivated user"
        )

    existing_student = (
        db.query(Student)
        .filter(Student.uid == uid)
        .first()
    )

    if existing_student:
        raise ValueError(
            "Student profile already exists for this user"
        )

    student = Student(
        uid=uid,
        name=student_data["name"],
        date_of_birth=student_data.get(
            "date_of_birth"
        ),
        gender=student_data.get("gender"),
        phone_number=student_data.get(
            "phone_number"
        )
    )

    try:
        db.add(student)
        db.commit()
        db.refresh(student)

    except Exception:
        db.rollback()
        raise

    return student


def update_student(
    db: Session,
    student_id: int,
    updated_data: dict
):
    student = get_student(
        db,
        student_id
    )

    if not student:
        return None

    for field, value in updated_data.items():
        setattr(
            student,
            field,
            value
        )

    try:
        db.commit()
        db.refresh(student)

    except Exception:
        db.rollback()
        raise

    return student


def delete_student(
    db: Session,
    student_id: int
):
    student = get_student(
        db,
        student_id
    )

    if not student:
        return None

    try:
        db.delete(student)
        db.commit()

    except Exception:
        db.rollback()
        raise

    return student