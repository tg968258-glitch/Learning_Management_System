from sqlalchemy.orm import Session

from Backend.src.models.class_session import ClassSession


class SessionRepository:

    @staticmethod
    def get_by_id(
        db: Session,
        session_id: int
    ) -> ClassSession | None:

        return (
            db.query(ClassSession)
            .filter(ClassSession.session_id == session_id)
            .first()
        )

    @staticmethod
    def get_by_course(
        db: Session,
        course_id: int
    ) -> list[ClassSession]:

        return (
            db.query(ClassSession)
            .filter(ClassSession.course_id == course_id)
            .order_by(
                ClassSession.session_date.asc(),
                ClassSession.start_time.asc()
            )
            .all()
        )

    @staticmethod
    def create(
        db: Session,
        session_data: dict
    ) -> ClassSession:

        session = ClassSession(
            course_id=session_data["course_id"],
            teacher_id=session_data.get("teacher_id"),
            session_date=session_data["session_date"],
            start_time=session_data.get("start_time"),
            end_time=session_data.get("end_time"),
            topic=session_data.get("topic"),
            meeting_link=session_data.get("meeting_link")
        )

        db.add(session)
        db.commit()
        db.refresh(session)

        return session

    @staticmethod
    def update(
        db: Session,
        session: ClassSession,
        update_data: dict
    ) -> ClassSession:

        for field, value in update_data.items():
            if hasattr(session, field) and value is not None:
                setattr(session, field, value)

        db.commit()
        db.refresh(session)

        return session

    @staticmethod
    def delete(
        db: Session,
        session: ClassSession
    ) -> None:

        db.delete(session)
        db.commit()