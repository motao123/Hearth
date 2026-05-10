import uuid
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from app.core.config import settings


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def create_token(user_id: int, hours: int | None = None) -> str:
    expire = datetime.now(timezone.utc) + timedelta(hours=hours or settings.session_expire_hours)
    return jwt.encode(
        {"sub": str(user_id), "exp": expire, "jti": uuid.uuid4().hex},
        settings.secret_key,
        algorithm="HS256",
    )


def decode_token(token: str) -> dict | None:
    try:
        return jwt.decode(
            token,
            settings.secret_key,
            algorithms=["HS256"],
            options={"require": ["sub", "exp", "jti"]},
        )
    except (jwt.InvalidTokenError, jwt.DecodeError):
        return None
