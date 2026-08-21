import hashlib
import os
import secrets
from datetime import datetime, timedelta, timezone

import jwt
from dotenv import load_dotenv
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash

load_dotenv()

password_hash = PasswordHash.recommended()


JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
)


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str
) -> bool:
    return password_hash.verify(
        plain_password,
        hashed_password
    )


def create_access_token(
    uid: str,
    role: str
) -> str:

    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": uid,
        "role": role,
        "exp": expires_at
    }

    return jwt.encode(
        payload,
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM
    )


def decode_access_token(token: str):

    try:
        return jwt.decode(
            token,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM]
        )

    except InvalidTokenError:
        return None


def create_refresh_token() -> str:
    return secrets.token_urlsafe(48)


def hash_refresh_token(token: str) -> str:
    return hashlib.sha256(
        token.encode()
    ).hexdigest()
