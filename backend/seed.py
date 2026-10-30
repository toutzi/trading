"""Seed test users. Data, not schema — run after `alembic upgrade head`."""

from app.database import Base, SessionLocal, engine
from app.models import User
from app.security import hash_password

SEED_USERS = [
    {"email": "alice@example.com", "password": "password123", "name": "Alice"},
    {"email": "bob@example.com", "password": "password123", "name": "Bob"},
]


def seed() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        for spec in SEED_USERS:
            existing = db.query(User).filter(User.email == spec["email"]).first()
            if existing:
                continue
            db.add(
                User(
                    email=spec["email"],
                    password_hash=hash_password(spec["password"]),
                    name=spec["name"],
                )
            )
        db.commit()
        print(f"Seeded {len(SEED_USERS)} users.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
