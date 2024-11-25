from dataclasses import dataclass

from faker import Faker
from sqlmodel import Session

from db.models.user import User, UserStatus
from security.hashing import get_password_hash


# We use a dataclass here for better editor/mypy support
@dataclass
class UserCredentials:
    username: str
    password: str


def generate_user(session: Session, status: UserStatus = UserStatus.PENDING_CONFIRMATION) -> tuple[User, UserCredentials]:
    """
    Generates a new fake user in `session`, and returns:
    - The user itself
    - Its credentials (which are important for accessing the unhashed password)

    This is useful for skipping the entire registration flow in tests that are not related to that
    """
    faker = Faker()

    original_password = faker.password(length=12)
    hashed_password = get_password_hash(original_password)

    user = User(
        email=faker.email(),
        username=faker.user_name(),
        password=hashed_password,
        name=faker.name(),
        birthday=faker.date_of_birth(),
        status=status
    )
    session.add(user)
    session.commit()

    credentials = UserCredentials(user.username, original_password)

    return (user, credentials)
