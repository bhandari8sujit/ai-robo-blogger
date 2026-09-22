import secrets
import string

from sqlmodel import Session

from app.core.database import create_db_and_tables, engine
from app.models import User
from app.security import get_password_hash


def _random_password(length: int = 20) -> str:
    alphabet = string.ascii_letters + string.digits + "-._"
    return "".join(secrets.choice(alphabet) for _ in range(length))


def seed_users(count: int = 5) -> tuple[str, str]:
    create_db_and_tables()
    credentials: list[tuple[str, str]] = []
    with Session(engine) as session:
        for _ in range(count):
            email = f"seed-{secrets.token_hex(6)}@example.com"
            password = _random_password()
            session.add(User(email=email, hashed_password=get_password_hash(password)))
            credentials.append((email, password))
        session.commit()
    return credentials[0]


if __name__ == "__main__":
    email, password = seed_users()
    print(f"Seeded 5 users. Test email: {email}")
    print(f"Test password: {password}")


## Test authentication with the following credentials:
# Email: seed-1fd47a2f5a94@example.com
# Password: cY322AcGIlZr68YtoKBR
