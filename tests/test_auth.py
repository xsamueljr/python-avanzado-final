from unittest.mock import Mock
from dataclasses import asdict

from fastapi.testclient import TestClient
from sqlmodel import Session, select

from .constants import Endpoints, VALID_PAYLOAD
from .utils import generate_user
from db.models.user import User, UserStatus
from db.models.confirmation_token import ConfirmationToken


def test_user_can_signup(client: TestClient, session: Session, mock_email_manager: Mock):
    response = client.post(Endpoints.REGISTER.value, json=VALID_PAYLOAD)
    body = response.json()
    email, link = mock_email_manager.mock_calls[0].args
    users_db = session.exec(select(User)).all()
    user = users_db[0]

    assert response.status_code == 201, response.text
    assert body["username"] == "cooluser"
    assert body["id"] is not None


    mock_email_manager.assert_called_once()
    assert email == VALID_PAYLOAD["email"]
    assert link is not None

    assert len(users_db) == 1
    assert user.email == VALID_PAYLOAD["email"]
    assert user.status == UserStatus.PENDING_CONFIRMATION


def test_user_can_confirm_registration(client: TestClient, session: Session, mock_email_manager: Mock):
    assert client.post(Endpoints.REGISTER.value, json=VALID_PAYLOAD).status_code == 201, "The user couldn't even register"
    user = session.exec(select(User)).first()
    assert user is not None, "User is not present in DB after registration"
    assert user.status == UserStatus.PENDING_CONFIRMATION, f"User status should be pending confirmation, but it's {user.status}"

    confirmation_token = session.exec(select(ConfirmationToken).where(ConfirmationToken.user_id == user.id)).first()
    assert confirmation_token is not None, "Confirmation token wasn't created"

    confirmation_link = Endpoints.CONFIRM.value.format(confirmation_token.token)

    response = client.get(confirmation_link)
    assert response.status_code == 200
    assert user.status == UserStatus.ACTIVE


def test_user_cannot_login_if_has_to_confirm(
    client: TestClient,
    session: Session,
):
    _, credentials = generate_user(session)

    response = client.post(Endpoints.LOGIN.value, data=asdict(credentials))
    
    assert response.status_code == 403, response.text
    assert "must be confirmed" in response.json()["detail"]
