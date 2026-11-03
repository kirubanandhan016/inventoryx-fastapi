from datetime import datetime, timedelta, timezone

import pytest
from jose import jwt
from pydantic import ValidationError

from app.core.config import Settings, get_settings
from app.core.security import ALGORITHM, decode_access_token


def test_register_login_and_read_profile(client):
    registration = client.post(
        "/auth/register",
        json={
            "email": "user@example.com",
            "full_name": "Test User",
            "password": "a-secure-password",
        },
    )
    assert registration.status_code == 201
    assert registration.json()["email"] == "user@example.com"
    assert "hashed_password" not in registration.json()

    login = client.post(
        "/auth/login",
        data={"username": "user@example.com", "password": "a-secure-password"},
    )
    assert login.status_code == 200
    token = login.json()["access_token"]

    profile = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert profile.status_code == 200
    assert profile.json()["full_name"] == "Test User"


def test_duplicate_registration_and_invalid_login(client):
    payload = {
        "email": "user@example.com",
        "full_name": "Test User",
        "password": "a-secure-password",
    }
    assert client.post("/auth/register", json=payload).status_code == 201
    assert client.post("/auth/register", json=payload).status_code == 409
    assert (
        client.post(
            "/auth/login",
            data={"username": "user@example.com", "password": "incorrect"},
        ).status_code
        == 401
    )


def test_protected_endpoint_requires_authentication(client):
    response = client.post(
        "/products",
        json={"sku": "SKU-1", "name": "Widget", "price": "2.50"},
    )
    assert response.status_code == 401


def test_issued_access_token_contains_required_claims(client):
    client.post(
        "/auth/register",
        json={
            "email": "claims@example.com",
            "full_name": "Claims Test",
            "password": "a-secure-password",
        },
    )
    response = client.post(
        "/auth/login",
        data={"username": "claims@example.com", "password": "a-secure-password"},
    )
    assert response.status_code == 200

    payload = jwt.decode(
        response.json()["access_token"],
        get_settings().secret_key,
        algorithms=[ALGORITHM],
    )
    assert payload["sub"].isdigit()
    assert isinstance(payload["iat"], int)
    assert isinstance(payload["exp"], int)


def test_access_token_without_iat_is_rejected():
    now = datetime.now(timezone.utc)
    token = jwt.encode(
        {"sub": "1", "exp": int((now + timedelta(minutes=5)).timestamp())},
        get_settings().secret_key,
        algorithm=ALGORITHM,
    )
    assert decode_access_token(token) is None


def test_access_token_without_exp_is_rejected():
    token = jwt.encode(
        {"sub": "1", "iat": int(datetime.now(timezone.utc).timestamp())},
        get_settings().secret_key,
        algorithm=ALGORITHM,
    )
    assert decode_access_token(token) is None


def test_access_token_with_non_numeric_subject_is_rejected():
    now = datetime.now(timezone.utc)
    token = jwt.encode(
        {
            "sub": "not-a-user-id",
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(minutes=5)).timestamp()),
        },
        get_settings().secret_key,
        algorithm=ALGORITHM,
    )
    assert decode_access_token(token) is None


def test_settings_reject_missing_or_short_secret(monkeypatch):
    monkeypatch.delenv("SECRET_KEY", raising=False)
    with pytest.raises(ValidationError):
        Settings(_env_file=None)
    with pytest.raises(ValidationError):
        Settings(_env_file=None, secret_key="too-short")


def test_settings_reject_non_positive_token_lifetime(monkeypatch):
    monkeypatch.setenv(
        "SECRET_KEY",
        "inventoryx-test-only-secret-key-never-use-in-production-48",
    )
    with pytest.raises(ValidationError):
        Settings(_env_file=None, access_token_expire_minutes=0)
