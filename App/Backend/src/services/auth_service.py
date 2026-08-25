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
from Backend.src.repositories.student_repository import StudentRepository
from Backend.src.repositories.user_repository import UserRepository
from Backend.src.services.email_service import send_otp_email

# Minimum seconds between resend requests
OTP_RESEND_COOLDOWN_SECONDS = 60


def generate_uid(db: Session) -> str:
    last_user = UserRepository.get_last_user(db)
    if not last_user:
        return "USR001"

    number = int(last_user.uid.replace("USR", ""))
    return f"USR{number + 1:03d}"


def register_user(
    db: Session,
    username: str,
    email: str,
    recovery_email: str | None,
    password: str,
    name: str,
):
    """
    Publicly accessible student registration.
    - Creates User with role='student'
    - Auto-creates Student profile with provided name
    - Sends email verification OTP via Brevo SMTP
    """
    existing_email = UserRepository.get_by_email(db, email)
    if existing_email:
        raise ValueError("User with this email already exists")

    existing_username = UserRepository.get_by_username(db, username)
    if existing_username:
        raise ValueError("Username already exists")

    if recovery_email and recovery_email == email:
        raise ValueError("Recovery email cannot be the same as primary email")

    uid = generate_uid(db)

    user_data = {
        "uid": uid,
        "username": username,
        "email": email,
        "recovery_email": recovery_email,
        "password_hash": hash_password(password),
        "role": "student",
        "email_verified": False,
        "recovery_email_verified": False,
        "is_active": True,
        "deactivated_at": None,
    }

    user = UserRepository.create(db, user_data)
    StudentRepository.create(db, {"uid": uid, "name": name})

    # Send verification OTP via email
    otp = create_otp(db, uid, "email_verification")
    send_otp_email(
        to_email=email,
        otp=otp,
        purpose="email_verification",
        username=username
    )

    return {
        "uid": user.uid,
        "username": user.username,
        "email": user.email,
        "role": user.role,
        "email_verified": user.email_verified,
        "is_active": user.is_active,
        "message": "Registration successful. A verification OTP has been sent to your email."
    }


def authenticate_user(
    db: Session,
    email: str,
    password: str,
    remember_me: bool = False
):
    email = email.strip().lower()
    user = UserRepository.get_by_email(db, email)

    if not user:
        return None

    if not verify_password(password, user.password_hash):
        return None

    if not user.is_active:
        raise ValueError("Your account is deactivated")

    access_token = create_access_token(
        uid=user.uid,
        role=user.role
    )

    session = create_user_session(db, user.uid, remember_me)

    return {
        "uid": user.uid,
        "username": user.username,
        "email": user.email,
        "role": user.role,
        "email_verified": user.email_verified,
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

    user = UserRepository.get_by_uid(db, uid)
    if not user:
        raise ValueError("User not found")

    # Invalidate any existing active OTPs for this purpose
    UserRepository.invalidate_existing_otps(db, uid, purpose)

    otp = generate_otp()
    UserRepository.create_otp_record(
        db=db,
        uid=uid,
        otp_hash=hash_otp(otp),
        purpose=purpose,
        expires_at=get_otp_expiry()
    )

    return otp


def verify_user_otp(
    db: Session,
    uid: str,
    purpose: str,
    otp: str
):
    otp_record = UserRepository.get_active_otp(db, uid, purpose)

    if not otp_record:
        raise ValueError("OTP not found")

    if otp_record.expires_at < datetime.utcnow():
        raise ValueError("OTP has expired")

    if otp_record.attempts >= 5:
        raise ValueError("Maximum OTP attempts exceeded")

    if not verify_otp(otp, otp_record.otp_hash):
        UserRepository.increment_otp_attempts(db, otp_record)
        raise ValueError("Invalid OTP")

    UserRepository.mark_otp_used(db, otp_record)
    return True


def request_email_verification(
    db: Session,
    email: str
):
    email = email.strip().lower()
    user = UserRepository.get_by_email(db, email)

    if not user:
        raise ValueError("User not found")

    if user.email_verified:
        raise ValueError("Email is already verified")

    otp = create_otp(db, user.uid, "email_verification")

    email_sent = send_otp_email(
        to_email=email,
        otp=otp,
        purpose="email_verification",
        username=user.username
    )

    if not email_sent:
        raise ValueError(
            "OTP was generated, but the verification email could not be sent."
        )

    return True


def resend_otp(
    db: Session,
    email: str,
    purpose: str
):
    allowed_purposes = [
        "email_verification",
        "password_reset",
        "recovery_email_verification"
    ]

    if purpose not in allowed_purposes:
        raise ValueError("Invalid OTP purpose")

    email = email.strip().lower()
    user = UserRepository.get_by_email(db, email)

    if not user:
        raise ValueError("User not found")

    if purpose == "email_verification" and user.email_verified:
        raise ValueError("Email is already verified")

    # Check cooldown
    last_otp = UserRepository.get_latest_otp(db, user.uid, purpose)
    if last_otp:
        elapsed = (datetime.utcnow() - last_otp.created_at).total_seconds()
        if elapsed < OTP_RESEND_COOLDOWN_SECONDS:
            remaining = int(OTP_RESEND_COOLDOWN_SECONDS - elapsed)
            raise ValueError(
                f"Please wait {remaining} seconds before requesting a new OTP."
            )

    otp = create_otp(db, user.uid, purpose)

    send_otp_email(
        to_email=email,
        otp=otp,
        purpose=purpose,
        username=user.username
    )

    return True


def verify_email(
    db: Session,
    email: str,
    otp: str
):
    email = email.strip().lower()
    user = UserRepository.get_by_email(db, email)

    if not user:
        raise ValueError("User not found")

    if user.email_verified:
        raise ValueError("Email is already verified")

    verify_user_otp(db, user.uid, "email_verification", otp)
    UserRepository.update(db, user, {"email_verified": True})
    return True


def request_password_reset(
    db: Session,
    email: str
):
    email = email.strip().lower()
    user = UserRepository.get_by_email(db, email)

    if not user:
        raise ValueError("User not found")

    if not user.is_active:
        raise ValueError("User account is deactivated")

    otp = create_otp(db, user.uid, "password_reset")

    send_otp_email(
        to_email=email,
        otp=otp,
        purpose="password_reset",
        username=user.username
    )

    return True


def reset_user_password(
    db: Session,
    email: str,
    otp: str,
    new_password: str
):
    email = email.strip().lower()
    user = UserRepository.get_by_email(db, email)

    if not user:
        raise ValueError("User not found")

    verify_user_otp(db, user.uid, "password_reset", otp)

    if verify_password(new_password, user.password_hash):
        raise ValueError("New password cannot be the same as old password")

    UserRepository.update(db, user, {"password_hash": hash_password(new_password)})
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
    session_id = str(uuid4())

    session = UserRepository.create_session(
        db=db,
        session_id=session_id,
        uid=uid,
        refresh_token_hash=hash_refresh_token(refresh_token),
        expires_at=expires_at
    )

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
    session = UserRepository.get_session_by_hash(db, hashed_token)

    if not session:
        raise ValueError("Invalid session")

    if session.expires_at < datetime.utcnow():
        raise ValueError("Session expired")

    user = UserRepository.get_by_uid(db, session.uid)
    if not user:
        raise ValueError("User not found")

    if not user.is_active:
        raise ValueError("User account is deactivated")

    UserRepository.update_session_usage(db, session)
    return create_access_token(uid=user.uid, role=user.role)


def logout_user(
    db: Session,
    session_id: str,
    uid: str
):
    session = UserRepository.get_active_session_by_id(db, session_id, uid)
    if not session:
        raise ValueError("Active session not found")

    UserRepository.revoke_session(db, session)
    return True
