import uuid
from datetime import timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models import User
from app.security import create_access_token, hash_password


@pytest.fixture
def db_engine():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    return engine


@pytest.fixture
def session_factory(db_engine):
    return sessionmaker(bind=db_engine, autoflush=False, autocommit=False)


@pytest.fixture
def client(db_engine, session_factory):
    def override_get_db():
        db = session_factory()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def make_user(session_factory):
    def _make(email="alice@example.com", password="password123", name="Alice"):
        db = session_factory()
        user = User(
            email=email,
            password_hash=hash_password(password),
            name=name,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        db.close()
        return user

    return _make


@pytest.fixture
def make_token(make_user):
    def _make(email="alice@example.com"):
        user = make_user(email=email)
        return create_access_token(str(user.id))

    return _make
