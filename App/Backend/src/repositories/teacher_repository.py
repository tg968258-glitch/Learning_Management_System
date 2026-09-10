from datetime import date, datetime
from sqlalchemy import func
from sqlalchemy.orm import Session

from Backend.src.models.assignment import Assignment
from Backend.src.models.class_session import ClassSession
from Backend.src.models.course import Course, CourseTeacher
from Backend.src.models.enrollment import Enrollment
from Backend.src.models.teacher import Teacher
from Backend.src.models.teacher_invitation import TeacherInvitation


class TeacherRepository:
    @staticmethod
    def get_dashboard_stats(db: Session, uid: str) -> dict:
        """Aggregate dashboard counts for the teacher identified by the auth UID."""
        row = db.query(
            db.query(func.count(func.distinct(Course.course_id)))
            .join(CourseTeacher, CourseTeacher.course_id == Course.course_id)
            .join(Teacher, Teacher.teacher_id == CourseTeacher.teacher_id)
            .filter(Teacher.uid == uid, Course.status == "active")
            .scalar_subquery()
            .label("active_courses"),
            db.query(func.count(func.distinct(Enrollment.student_id)))
            .join(CourseTeacher, CourseTeacher.course_id == Enrollment.course_id)
            .join(Teacher, Teacher.teacher_id == CourseTeacher.teacher_id)
            .filter(Teacher.uid == uid, Enrollment.status == "active")
            .scalar_subquery()
            .label("total_students"),
            db.query(func.count(func.distinct(Assignment.assignment_id)))
            .join(CourseTeacher, CourseTeacher.course_id == Assignment.course_id)
            .join(Teacher, Teacher.teacher_id == CourseTeacher.teacher_id)
            .filter(Teacher.uid == uid)
            .scalar_subquery()
            .label("assignments"),
            db.query(func.count(func.distinct(ClassSession.session_id)))
            .join(Teacher, Teacher.teacher_id == ClassSession.teacher_id)
            .filter(Teacher.uid == uid, ClassSession.session_date >= date.today())
            .scalar_subquery()
            .label("live_sessions"),
        ).one()
        return {key: int(value or 0) for key, value in row._mapping.items()}

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
            status="Pending",
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
                TeacherInvitation.is_used == False,
                TeacherInvitation.status == "Pending"
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
                TeacherInvitation.status == "Pending",
                TeacherInvitation.expires_at > datetime.utcnow()
            )
            .first()
        )

    @staticmethod
    def mark_invitation_used(db: Session, invitation: TeacherInvitation) -> None:
        invitation.is_used = True
        invitation.status = "Accepted"
        db.commit()

    @staticmethod
    def expire_pending_invitations(db: Session) -> None:
        db.query(TeacherInvitation).filter(
            TeacherInvitation.status == "Pending",
            TeacherInvitation.expires_at <= datetime.utcnow(),
        ).update({"status": "Rejected"}, synchronize_session=False)
        db.commit()

    @staticmethod
    def get_invitations(db: Session) -> list[TeacherInvitation]:
        TeacherRepository.expire_pending_invitations(db)
        return db.query(TeacherInvitation).order_by(TeacherInvitation.created_at.desc()).all()
