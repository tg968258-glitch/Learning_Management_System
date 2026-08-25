from datetime import datetime
from sqlalchemy.orm import Session

from Backend.src.models.teacher import Teacher
from Backend.src.models.teacher_invitation import TeacherInvitation


class TeacherRepository:
    @staticmethod
    def get_by_id(db: Session, teacher_id: int) -> Teacher | None:
        return db.query(Teacher).filter(Teacher.teacher_id == teacher_id).first()

    @staticmethod
    def get_by_uid(db: Session, uid: str) -> Teacher | None:
        return db.query(Teacher).filter(Teacher.uid == uid).first()

    @staticmethod
    def get_all(
        db: Session,
        specialization: str | None = None
    ) -> list[Teacher]:
        query = db.query(Teacher)
        if specialization:
            query = query.filter(Teacher.specialization == specialization)
        return query.all()

    @staticmethod
    def count(db: Session) -> int:
        return db.query(Teacher).count()

    @staticmethod
    def create(db: Session, teacher_data: dict) -> Teacher:
        teacher = Teacher(
            uid=teacher_data["uid"],
            name=teacher_data["name"],
            phone_number=teacher_data.get("phone_number"),
            specialization=teacher_data.get("specialization"),
            qualification=teacher_data.get("qualification"),
            experience=teacher_data.get("experience")
        )
        db.add(teacher)
        db.commit()
        db.refresh(teacher)
        return teacher

    @staticmethod
    def update(db: Session, teacher: Teacher, update_data: dict) -> Teacher:
        for field, value in update_data.items():
            if hasattr(teacher, field) and value is not None:
                setattr(teacher, field, value)
        db.commit()
        db.refresh(teacher)
        return teacher

    @staticmethod
    def delete(db: Session, teacher: Teacher) -> None:
        db.delete(teacher)
        db.commit()

    # --- Teacher Invitations ---
    @staticmethod
    def create_invitation(
        db: Session,
        email: str,
        token_hash: str,
        expires_at: datetime,
        invited_by_uid: str
    ) -> TeacherInvitation:
        invitation = TeacherInvitation(
            email=email,
            token_hash=token_hash,
            invited_by=invited_by_uid,
            expires_at=expires_at,
            is_used=False,
            created_at=datetime.utcnow()
        )
        db.add(invitation)
        db.commit()
        db.refresh(invitation)
        return invitation

    @staticmethod
    def get_invitation_by_token_hash(db: Session, token_hash: str) -> TeacherInvitation | None:
        return db.query(TeacherInvitation).filter(TeacherInvitation.token_hash == token_hash).first()

    @staticmethod
    def get_active_invitation_by_token_hash(db: Session, token_hash: str) -> TeacherInvitation | None:
        return (
            db.query(TeacherInvitation)
            .filter(
                TeacherInvitation.token_hash == token_hash,
                TeacherInvitation.is_used == False
            )
            .first()
        )

    @staticmethod
    def get_active_invitation_by_email(db: Session, email: str) -> TeacherInvitation | None:
        return (
            db.query(TeacherInvitation)
            .filter(
                TeacherInvitation.email == email,
                TeacherInvitation.is_used == False,
                TeacherInvitation.expires_at > datetime.utcnow()
            )
            .first()
        )

    @staticmethod
    def mark_invitation_used(db: Session, invitation: TeacherInvitation) -> None:
        invitation.is_used = True
        db.commit()
