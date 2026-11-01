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


def validate_secret_key() -> str:
    """Return the configured JWT key, rejecting empty or weak defaults."""
    secret_key = get_settings().secret_key
    if len(secret_key.encode("utf-8")) < 32:
        raise RuntimeError(
            "SECRET_KEY must be configured with at least 32 bytes. "
            "Generate a unique value and store it in your local .env file."
        )
    return secret_key


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
        if scheme != "pbkdf2_sha256":
            return False
        salt = base64.urlsafe_b64decode(salt_encoded.encode())
        expected = base64.urlsafe_b64decode(digest_encoded.encode())
        actual = hashlib.pbkdf2_hmac(
            _HASH_NAME, password.encode(), salt, int(iterations)
        )
        return hmac.compare_digest(actual, expected)
    except (ValueError, TypeError):
        return False


def create_access_token(subject: str) -> str:
    expires = datetime.now(timezone.utc) + timedelta(
        minutes=get_settings().access_token_expire_minutes
    )
    return jwt.encode(
        {"sub": subject, "exp": expires},
        validate_secret_key(),
        algorithm=ALGORITHM,
    )


def decode_access_token(token: str) -> str | None:
    try:
        payload = jwt.decode(
            token, validate_secret_key(), algorithms=[ALGORITHM]
        )
        subject = payload.get("sub")
        return subject if isinstance(subject, str) else None
    except JWTError:
        return None
