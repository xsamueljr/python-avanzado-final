from dataclasses import asdict

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from .utils import generate_user
from .constants import Endpoints
from db.models.follow import Follow
from db.models.user import UserStatus


def test_user_cannot_follow_itself(client: TestClient, session: Session):
    user, credentials = generate_user(session, UserStatus.ACTIVE)
    login_response = client.post(Endpoints.LOGIN.value, data=asdict(credentials))
    access_token = login_response.json()["access_token"]

    endpoint = Endpoints.FOLLOW_USER.value.format(user.id)
    response = client.post(endpoint, headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 400
    assert "cannot follow yourself" in response.json()["detail"].lower()


def test_user_cannot_follow_inactive_user(client: TestClient, session: Session):
    _, credentials = generate_user(session, UserStatus.ACTIVE)
    user2, _ = generate_user(session, UserStatus.PENDING_CONFIRMATION)

    # User logs in
    login_response = client.post(Endpoints.LOGIN.value, data=asdict(credentials))
    access_token = login_response.json()["access_token"]

    # Users tries to follow inactive user
    endpoint = Endpoints.FOLLOW_USER.value.format(user2.id)
    response = client.post(
        endpoint,
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 400

    follows_db = session.exec(select(Follow)).all()
    assert len(follows_db) == 0
