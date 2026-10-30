from datetime import datetime, timedelta, timezone

import jwt

from app.config import settings


def test_me_with_valid_token_returns_profile(client, make_token):
    token = make_token(email="alice@example.com")
    r = client.get("/me", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    body = r.json()
    assert body["email"] == "alice@example.com"
    assert body["name"] == "Alice"
    assert body["id"]
    assert body["created_at"].endswith("Z")
    assert set(body.keys()) == {"id", "email", "name", "created_at"}


def test_me_missing_token_returns_unauthorized(client):
    r = client.get("/me")
    assert r.status_code == 401
    assert r.json()["error"]["code"] == "unauthorized"


def test_me_malformed_token_returns_invalid_token(client):
    r = client.get("/me", headers={"Authorization": "Bearer not.a.jwt"})
    assert r.status_code == 401
    assert r.json()["error"]["code"] == "invalid_token"


def test_me_expired_token_returns_invalid_token(client, make_user):
    user = make_user(email="alice@example.com")
    exp = datetime.now(timezone.utc) - timedelta(seconds=1)
    token = jwt.encode(
        {"sub": str(user.id), "exp": exp},
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )
    r = client.get("/me", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 401
    assert r.json()["error"]["code"] == "invalid_token"


def test_me_token_for_unknown_user_returns_invalid_token(client):
    from app.security import create_access_token

    token = create_access_token("00000000-0000-0000-0000-000000000000")
    r = client.get("/me", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 401
    assert r.json()["error"]["code"] == "invalid_token"
