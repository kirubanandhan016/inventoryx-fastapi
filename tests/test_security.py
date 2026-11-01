import pytest

from app.core.config import get_settings
from app.core.security import create_access_token, validate_secret_key


def test_jwt_secret_must_be_at_least_32_bytes(monkeypatch):
    monkeypatch.setattr(get_settings(), "secret_key", "too-short")

    with pytest.raises(RuntimeError, match="SECRET_KEY"):
        validate_secret_key()


def test_access_token_can_be_created_with_configured_secret(monkeypatch):
    monkeypatch.setattr(
        get_settings(),
        "secret_key",
        "test-only-secret-key-with-at-least-32-bytes",
    )

    token = create_access_token("123")

    assert isinstance(token, str)
    assert token
