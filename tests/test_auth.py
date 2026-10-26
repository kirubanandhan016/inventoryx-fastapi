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
    assert client.post(
        "/products",
        json={"sku": "SKU-1", "name": "Widget", "price": "2.50"},
    ).status_code == 401
