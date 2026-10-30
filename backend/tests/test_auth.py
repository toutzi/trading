def test_login_success_returns_token(client, make_user):
    make_user(email="alice@example.com", password="password123")
    r = client.post(
        "/auth/login",
        json={"email": "alice@example.com", "password": "password123"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["token_type"] == "bearer"
    assert body["expires_in"] == 900
    assert isinstance(body["access_token"], str) and body["access_token"]
    # exact envelope keys, no extra fields
    assert set(body.keys()) == {"access_token", "token_type", "expires_in"}


def test_login_wrong_password_returns_envelope(client, make_user):
    make_user(email="alice@example.com", password="password123")
    r = client.post(
        "/auth/login",
        json={"email": "alice@example.com", "password": "wrong"},
    )
    assert r.status_code == 401
    assert r.json() == {
        "error": {"code": "invalid_credentials", "message": "Invalid email or password"}
    }


def test_login_unknown_email_returns_envelope(client):
    r = client.post(
        "/auth/login",
        json={"email": "nobody@example.com", "password": "whatever"},
    )
    assert r.status_code == 401
    assert r.json()["error"]["code"] == "invalid_credentials"


def test_login_missing_field_returns_validation_error(client):
    r = client.post("/auth/login", json={"email": "alice@example.com"})
    assert r.status_code == 422
    assert r.json()["error"]["code"] == "validation_error"


def test_login_invalid_email_returns_validation_error(client):
    r = client.post(
        "/auth/login",
        json={"email": "not-an-email", "password": "x"},
    )
    assert r.status_code == 422
    assert r.json()["error"]["code"] == "validation_error"
