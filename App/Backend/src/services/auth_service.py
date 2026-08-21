from datetime import datetime, timedelta
from uuid import uuid4

from sqlalchemy.orm import Session

from Backend.src.core.otp_utils import (
    generate_otp,
    get_otp_expiry,
    hash_otp,
    verify_otp,
)
from Backend.src.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    hash_refresh_token,
    verify_password,
)
from Backend.src.models.user import OTPVerification, User, UserSession


def generate_uid(db: Session):

    last_user = (
        db.query(User)
        .order_by(User.uid.desc())
        .first()
    )

    if not last_user:
        return "USR001"

    number = int(
        last_user.uid.replace("USR", "")
    )

    return f"USR{number + 1:03d}"


def register_user(
    db: Session,
    username: str,
    email: str,
    recovery_email: str | None,
    password: str,
    role: str
):

    existing_email = (
        db.query(User)
        .filter(User.email == email)
        .first()
    )

    if existing_email:
        raise ValueError(
            "User with this email already exists"
        )

    existing_username = (
        db.query(User)
        .filter(User.username == username)
        .first()
    )


    if existing_username:
        raise ValueError(
            "Username already exists"
        )

    if recovery_email == email:
       raise ValueError(
        "Recovery email cannot be the same as primary email"
    )


    if role not in [
        "teacher",
        "student"
    ]:
        raise ValueError(
            "Role must be teacher or student"
        )

    uid = generate_uid(db)

    user = User(
        uid=uid,
        username=username,
        email=email,
        recovery_email=recovery_email,
        password_hash=hash_password(password),
        role=role,
        email_verified=False,
        recovery_email_verified=False,
        is_active=True,
        deactivated_at=None
    )

    try:
        db.add(user)
        db.commit()
        db.refresh(user)

    except Exception:
        db.rollback()
        raise
    return {
    "uid": user.uid,
    "username": user.username,
    "email": user.email,
    "recovery_email": user.recovery_email,
    "role": user.role,
    "email_verified": user.email_verified,
    "recovery_email_verified": user.recovery_email_verified,
    "is_active": user.is_active
}
    

def authenticate_user(
    db: Session,
    email: str,
    password: str,
    remember_me: bool = False
):
    email = email.strip().lower()

    user = (
        db.query(User)
        .filter(User.email == email)
        .first()
    )

    if not user:
        return None

    if not verify_password(
        password,
        user.password_hash
    ):
        return None

    if not user.is_active:
        raise ValueError(
            "Your account is deactivated"
        )

    access_token = create_access_token(
        uid=user.uid,
        role=user.role
    )

    session = create_user_session(
        db,
        user.uid,
        remember_me
    )

    return {
        "uid": user.uid,
        "username": user.username,
        "email": user.email,
        "role": user.role,
        "access_token": access_token,
        "refresh_token": session["refresh_token"],
        "session_id": session["session_id"],
        "token_type": "bearer"
    }

def create_otp(
    db: Session,
    uid: str,
    purpose: str
):
    allowed_purposes = [
        "email_verification",
        "password_reset",
        "recovery_email_verification"
    ]

    if purpose not in allowed_purposes:
        raise ValueError("Invalid OTP purpose")

    user = (
        db.query(User)
        .filter(User.uid == uid)
        .first()
    )

    if not user:
        raise ValueError("User not found")

    db.query(OTPVerification).filter(
    OTPVerification.uid == uid,
    OTPVerification.purpose == purpose,
    OTPVerification.is_used == False
).update(
    {"is_used": True},
    synchronize_session=False
)

    otp = generate_otp()

    otp_record = OTPVerification(
        uid=uid,
        otp_hash=hash_otp(otp),
        purpose=purpose,
        expires_at=get_otp_expiry(),
        attempts=0,
        is_used=False
    )

    db.add(otp_record)

    try:
        db.commit()
        db.refresh(otp_record)

    except Exception:
        db.rollback()
        raise

    return otp

def verify_user_otp(
    db: Session,
    uid: str,
    purpose: str,
    otp: str
):
    otp_record = (
        db.query(OTPVerification)
        .filter(
            OTPVerification.uid == uid,
            OTPVerification.purpose == purpose,
            OTPVerification.is_used == False
        )
        .order_by(
            OTPVerification.created_at.desc()
        )
        .first()
    )

    if not otp_record:
        raise ValueError(
            "OTP not found"
        )

    if otp_record.expires_at < datetime.utcnow():
        raise ValueError(
            "OTP has expired"
        )

    if otp_record.attempts >= 5:
        raise ValueError(
            "Maximum OTP attempts exceeded"
        )

    if not verify_otp(
        otp,
        otp_record.otp_hash
    ):
        otp_record.attempts += 1
        db.commit()

        raise ValueError(
            "Invalid OTP"
        )

    otp_record.is_used = True
    db.commit()
    return True

def request_email_verification(
    db: Session,
    email: str
):
    email = email.strip().lower()

    user = (
        db.query(User)
        .filter(User.email == email)
        .first()
    )

    if not user:
        raise ValueError("User not found")

    if user.email_verified:
        raise ValueError("Email is already verified")

    otp = create_otp(
        db,
        user.uid,
        "email_verification"
    )

    return otp

def verify_email(
    db: Session,
    email: str,
    otp: str
):
    email = email.strip().lower()

    user = (
        db.query(User)
        .filter(User.email == email)
        .first()
    )

    if not user:
        raise ValueError("User not found")

    if user.email_verified:
        raise ValueError("Email is already verified")

    verify_user_otp(
        db,
        user.uid,
        "email_verification",
        otp
    )

    user.email_verified = True

    try:
        db.commit()
        db.refresh(user)

    except Exception:
        db.rollback()
        raise

    return True

def request_password_reset(
    db: Session,
    email: str
):
    email = email.strip().lower()

    user = (
        db.query(User)
        .filter(User.email == email)
        .first()
    )

    if not user:
        raise ValueError("User not found")

    if not user.is_active:
        raise ValueError("User account is deactivated")

    otp = create_otp(
        db,
        user.uid,
        "password_reset"
    )

    return otp


def reset_user_password(
    db: Session,
    email: str,
    otp: str,
    new_password: str
):
    email = email.strip().lower()

    user = (
        db.query(User)
        .filter(User.email == email)
        .first()
    )

    if not user:
        raise ValueError("User not found")

    verify_user_otp(
        db,
        user.uid,
        "password_reset",
        otp
    )

    if verify_password(
        new_password,
        user.password_hash
    ):
        raise ValueError(
            "New password cannot be the same as old password"
        )

    user.password_hash = hash_password(
        new_password
    )

    try:
        db.commit()
        db.refresh(user)

    except Exception:
        db.rollback()
        raise

    return True

def create_user_session(
    db: Session,
    uid: str,
    remember_me: bool = False
):
    refresh_token = create_refresh_token()

    expires_at = datetime.utcnow() + timedelta(
    days=30 if remember_me else 7
)

    session = UserSession(
        session_id=str(uuid4()),
        uid=uid,
        refresh_token_hash=hash_refresh_token(
            refresh_token
        ),
        created_at=datetime.utcnow(),
        expires_at=expires_at,
        revoked=False
    )

    try:
        db.add(session)
        db.commit()
        db.refresh(session)

    except Exception:
        db.rollback()
        raise

    return {
        "session_id": session.session_id,
        "refresh_token": refresh_token,
        "expires_at": session.expires_at
    }

def refresh_access_token(
    db: Session,
    refresh_token: str
):
    hashed_token = hash_refresh_token(refresh_token)

    session = (
        db.query(UserSession)
        .filter(
            UserSession.refresh_token_hash == hashed_token,
            UserSession.revoked == False
        )
        .first()
    )

    if not session:
        raise ValueError("Invalid session")

    if session.expires_at < datetime.utcnow():
        raise ValueError("Session expired")

    user = (
        db.query(User)
        .filter(User.uid == session.uid)
        .first()
    )

    if not user:
        raise ValueError("User not found")

    if not user.is_active:
        raise ValueError(
            "User account is deactivated"
        )

    session.last_used_at = datetime.utcnow()

    access_token = create_access_token(
        uid=user.uid,
        role=user.role
    )

    try:
        db.commit()

    except Exception:
        db.rollback()
        raise

    return access_token

def logout_user(
    db: Session,
    session_id: str,
    uid: str
):
    session = (
        db.query(UserSession)
        .filter(
            UserSession.session_id == session_id,
            UserSession.uid == uid,
            UserSession.revoked == False
        )
        .first()
    )

    if not session:
        raise ValueError(
            "Active session not found"
        )

    session.revoked = True

    try:
        db.commit()

    except Exception:
        db.rollback()
        raise

    return True

