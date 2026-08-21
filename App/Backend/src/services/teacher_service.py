from sqlalchemy.orm import Session

from Backend.src.models.teacher import Teacher
from Backend.src.models.user import User


def get_all_teachers(db: Session):
    return db.query(Teacher).all()


def get_teacher(
    db: Session,
    teacher_id: int
):
    return (
        db.query(Teacher)
        .filter(Teacher.teacher_id == teacher_id)
        .first()
    )


def create_teacher(
    db: Session,
    teacher_data: dict
):
    uid = teacher_data["uid"]

    user = (
        db.query(User)
        .filter(User.uid == uid)
        .first()
    )

    if not user:
        raise ValueError(
            "User with this UID does not exist"
        )

    if user.role != "teacher":
        raise ValueError(
            "This user does not have teacher role"
        )

    if not user.is_active:
        raise ValueError(
            "Cannot create profile for a deactivated user"
        )

    existing_teacher = (
        db.query(Teacher)
        .filter(Teacher.uid == uid)
        .first()
    )

    if existing_teacher:
        raise ValueError(
            "Teacher profile already exists for this user"
        )

    teacher = Teacher(
        uid=uid,
        name=teacher_data["name"],
        phone_number=teacher_data.get(
            "phone_number"
        ),
        specialization=teacher_data.get(
            "specialization"
        ),
        qualification=teacher_data.get(
            "qualification"
        ),
        experience=teacher_data.get(
            "experience"
        )
    )

    try:
        db.add(teacher)
        db.commit()
        db.refresh(teacher)

    except Exception:
        db.rollback()
        raise

    return teacher


def update_teacher(
    db: Session,
    teacher_id: int,
    updated_data: dict
):
    teacher = get_teacher(
        db,
        teacher_id
    )

    if not teacher:
        return None

    for field, value in updated_data.items():
        setattr(
            teacher,
            field,
            value
        )

    try:
        db.commit()
        db.refresh(teacher)

    except Exception:
        db.rollback()
        raise

    return teacher


def delete_teacher(
    db: Session,
    teacher_id: int
):
    teacher = get_teacher(
        db,
        teacher_id
    )

    if not teacher:
        return None

    try:
        db.delete(teacher)
        db.commit()

    except Exception:
        db.rollback()
        raise

    return teacher