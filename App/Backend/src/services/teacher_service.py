from sqlalchemy.orm import Session

from Backend.src.models.teacher import Teacher
from Backend.src.repositories.teacher_repository import TeacherRepository
from Backend.src.repositories.user_repository import UserRepository


def get_all_teachers(db: Session) -> list[Teacher]:
    return TeacherRepository.get_all(db)


def get_teacher(
    db: Session,
    teacher_id: int
) -> Teacher | None:
    return TeacherRepository.get_by_id(db, teacher_id)


def create_teacher(
    db: Session,
    teacher_data: dict
) -> Teacher:
    uid = teacher_data["uid"]

    user = UserRepository.get_by_uid(db, uid)
    if not user:
        raise ValueError("User with this UID does not exist")

    if user.role != "teacher":
        raise ValueError("This user does not have teacher role")

    if not user.is_active:
        raise ValueError("Cannot create profile for a deactivated user")

    existing_teacher = TeacherRepository.get_by_uid(db, uid)
    if existing_teacher:
        raise ValueError("Teacher profile already exists for this user")

    return TeacherRepository.create(db, teacher_data)


def update_teacher(
    db: Session,
    teacher_id: int,
    updated_data: dict
) -> Teacher | None:
    teacher = TeacherRepository.get_by_id(db, teacher_id)
    if not teacher:
        return None

    return TeacherRepository.update(db, teacher, updated_data)


def delete_teacher(
    db: Session,
    teacher_id: int
) -> Teacher | None:
    teacher = TeacherRepository.get_by_id(db, teacher_id)
    if not teacher:
        return None

    TeacherRepository.delete(db, teacher)
    return teacher