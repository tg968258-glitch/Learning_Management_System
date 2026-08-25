import secrets
from datetime import datetime, timedelta, timezone

from pwdlib import PasswordHash

otp_hash = PasswordHash.recommended()


def generate_otp() -> str:
    return f"{secrets.randbelow(1000000):06d}"


def hash_otp(otp: str) -> str:
    return otp_hash.hash(otp)


def verify_otp(
    plain_otp: str,
    hashed_otp: str
) -> bool:
    return otp_hash.verify(
        plain_otp,
        hashed_otp
    )


def get_otp_expiry():
    return datetime.now(timezone.utc) + timedelta(
        minutes=2
    )
