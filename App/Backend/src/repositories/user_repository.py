from datetime import datetime
from sqlalchemy.orm import Session

from Backend.src.models.user import OTPVerification, User, UserSession


class UserRepository:
    @staticmethod
    def get_by_id(db: Session, user_id: int) -> User | None:
        # Note: uid is primary key
        return db.query(User).filter(User.uid == str(user_id)).first()

    @staticmethod
    def get_by_uid(db: Session, uid: str) -> User | None:
        return db.query(User).filter(User.uid == uid).first()

    @staticmethod
    def get_by_email(db: Session, email: str) -> User | None:
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def get_by_username(db: Session, username: str) -> User | None:
        return db.query(User).filter(User.username == username).first()

    @staticmethod
    def get_last_user(db: Session) -> User | None:
        return db.query(User).order_by(User.uid.desc()).first()

    @staticmethod
    def get_all(
        db: Session,
        role: str | None = None,
        is_active: bool | None = None
    ) -> list[User]:
        query = db.query(User)
        if role:
            query = query.filter(User.role == role)
        if is_active is not None:
            query = query.filter(User.is_active == is_active)
        return query.all()

    @staticmethod
    def count_users(db: Session, role: str | None = None) -> int:
        query = db.query(User)
        if role:
            query = query.filter(User.role == role)
        return query.count()

    @staticmethod
    def create(db: Session, user_data: dict) -> User:
        user = User(**user_data)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def update(db: Session, user: User, update_data: dict) -> User:
        for field, value in update_data.items():
            if hasattr(user, field) and value is not None:
                setattr(user, field, value)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def delete(db: Session, user: User) -> None:
        db.delete(user)
        db.commit()

    # --- OTP Operations ---
    @staticmethod
    def invalidate_existing_otps(db: Session, uid: str, purpose: str) -> None:
        db.query(OTPVerification).filter(
            OTPVerification.uid == uid,
            OTPVerification.purpose == purpose,
            OTPVerification.is_used == False
        ).update(
            {"is_used": True},
            synchronize_session=False
        )
        db.commit()

    @staticmethod
    def create_otp_record(
        db: Session,
        uid: str,
        otp_hash: str,
        purpose: str,
        expires_at: datetime
    ) -> OTPVerification:
        otp_record = OTPVerification(
            uid=uid,
            otp_hash=otp_hash,
            purpose=purpose,
            expires_at=expires_at,
            attempts=0,
            is_used=False
        )
        db.add(otp_record)
        db.commit()
        db.refresh(otp_record)
        return otp_record

    @staticmethod
    def get_latest_otp(
        db: Session,
        uid: str,
        purpose: str
    ) -> OTPVerification | None:
        return (
            db.query(OTPVerification)
            .filter(
                OTPVerification.uid == uid,
                OTPVerification.purpose == purpose
            )
            .order_by(OTPVerification.created_at.desc())
            .first()
        )

    @staticmethod
    def get_active_otp(
        db: Session,
        uid: str,
        purpose: str
    ) -> OTPVerification | None:
        return (
            db.query(OTPVerification)
            .filter(
                OTPVerification.uid == uid,
                OTPVerification.purpose == purpose,
                OTPVerification.is_used == False
            )
            .order_by(OTPVerification.created_at.desc())
            .first()
        )

    @staticmethod
    def increment_otp_attempts(db: Session, otp_record: OTPVerification) -> None:
        otp_record.attempts += 1
        db.commit()

    @staticmethod
    def mark_otp_used(db: Session, otp_record: OTPVerification) -> None:
        otp_record.is_used = True
        db.commit()

    # --- Session Operations ---
    @staticmethod
    def create_session(
        db: Session,
        session_id: str,
        uid: str,
        refresh_token_hash: str,
        expires_at: datetime
    ) -> UserSession:
        session = UserSession(
            session_id=session_id,
            uid=uid,
            refresh_token_hash=refresh_token_hash,
            created_at=datetime.utcnow(),
            expires_at=expires_at,
            revoked=False
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        return session

    @staticmethod
    def get_session_by_hash(
        db: Session,
        refresh_token_hash: str
    ) -> UserSession | None:
        return (
            db.query(UserSession)
            .filter(
                UserSession.refresh_token_hash == refresh_token_hash,
                UserSession.revoked == False
            )
            .first()
        )

    @staticmethod
    def get_active_session_by_id(
        db: Session,
        session_id: str,
        uid: str
    ) -> UserSession | None:
        return (
            db.query(UserSession)
            .filter(
                UserSession.session_id == session_id,
                UserSession.uid == uid,
                UserSession.revoked == False
            )
            .first()
        )

    @staticmethod
    def update_session_usage(db: Session, session: UserSession) -> None:
        session.last_used_at = datetime.utcnow()
        db.commit()

    @staticmethod
    def revoke_session(db: Session, session: UserSession) -> None:
        session.revoked = True
        db.commit()
