import base64
import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt

from app.core.config import get_settings

ALGORITHM = "HS256"
_HASH_NAME = "sha256"
_ITERATIONS = 600_000


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac(_HASH_NAME, password.encode(), salt, _ITERATIONS)
    return "pbkdf2_sha256${}${}${}".format(
        _ITERATIONS,
        base64.urlsafe_b64encode(salt).decode(),
        base64.urlsafe_b64encode(digest).decode(),
    )


def verify_password(password: str, password_hash: str) -> bool:
    try:
        scheme, iterations, salt_encoded, digest_encoded = password_hash.split("$")
        if scheme != "pbkdf2_sha256" or int(iterations) != _ITERATIONS:
            return False
        salt = base64.urlsafe_b64decode(salt_encoded.encode())
        expected = base64.urlsafe_b64decode(digest_encoded.encode())
        actual = hashlib.pbkdf2_hmac(
            _HASH_NAME, password.encode(), salt, _ITERATIONS
        )
        return hmac.compare_digest(actual, expected)
    except (ValueError, TypeError):
        return False


def create_access_token(subject: str) -> str:
    settings = get_settings()
    now = datetime.now(timezone.utc)
    expires = now + timedelta(minutes=settings.access_token_expire_minutes)
    return jwt.encode(
        {
            "sub": str(subject),
            "iat": int(now.timestamp()),
            "exp": int(expires.timestamp()),
        },
        settings.secret_key,
        algorithm=ALGORITHM,
    )


def decode_access_token(token: str) -> str | None:
    try:
        payload = jwt.decode(
            token,
            get_settings().secret_key,
            algorithms=[ALGORITHM],
        )
        subject = payload.get("sub")
        issued_at = payload.get("iat")
        expires_at = payload.get("exp")

        # Require a numeric user ID and explicit, well-formed time claims.
        if not isinstance(subject, str) or not subject.isdigit():
            return None
        if isinstance(issued_at, bool) or not isinstance(issued_at, int):
            return None
        if isinstance(expires_at, bool) or not isinstance(expires_at, int):
            return None
        if expires_at <= issued_at:
            return None
        return subject
    except (JWTError, TypeError, ValueError):
        return None
