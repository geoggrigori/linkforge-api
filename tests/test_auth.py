"""Tests for the authentication flow."""


def test_register_creates_user(client):
    res = client.post(
        "/auth/register",
        json={"email": "bob@example.com", "password": "password123"},
    )
    assert res.status_code == 201
    body = res.json()
    assert body["email"] == "bob@example.com"
    assert "password" not in body  # never leak the password/hash


def test_register_duplicate_email_conflicts(client):
    creds = {"email": "dup@example.com", "password": "password123"}
    assert client.post("/auth/register", json=creds).status_code == 201
    assert client.post("/auth/register", json=creds).status_code == 409


def test_register_rejects_short_password(client):
    res = client.post(
        "/auth/register", json={"email": "x@example.com", "password": "short"}
    )
    assert res.status_code == 422  # validation error


def test_login_returns_token(client):
    creds = {"email": "carol@example.com", "password": "password123"}
    client.post("/auth/register", json=creds)
    res = client.post("/auth/login", json=creds)
    assert res.status_code == 200
    assert res.json()["token_type"] == "bearer"
    assert res.json()["access_token"]


def test_login_wrong_password_unauthorized(client):
    creds = {"email": "dave@example.com", "password": "password123"}
    client.post("/auth/register", json=creds)
    res = client.post(
        "/auth/login", json={"email": "dave@example.com", "password": "wrongpass1"}
    )
    assert res.status_code == 401


def test_protected_route_requires_token(client):
    assert client.get("/links").status_code == 401
