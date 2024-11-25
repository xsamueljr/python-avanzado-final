from unittest.mock import Mock
from dataclasses import asdict

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from db.models.like import Like

from .constants import VALID_PAYLOAD, Endpoints
from .utils import generate_user
from db.models.user import User, UserStatus
from db.models.post import Post, PostStatus


def test_user_can_post(client: TestClient, session: Session):
    # All authentication flows are tested elsewhere
    user, credentials = generate_user(session, status=UserStatus.ACTIVE)
    
    content = "THIS IS WORKING!!"
    payload = {
        "content": content
    }
    
    login_response = client.post(Endpoints.LOGIN.value, data=asdict(credentials))
    assert login_response.status_code == 200, login_response.text
    
    access_token = login_response.json()["access_token"]
    post_response = client.post(Endpoints.NEW_POST.value, json=payload, headers={"Authorization": f"Bearer {access_token}"})
    assert post_response.status_code == 201

    posts_db = session.exec(select(Post)).all()
    post = posts_db[0]

    assert post.author_id == user.id
    assert post.likes_count == 0
    assert post.status == PostStatus.PUBLIC


def test_user_can_like_other_posts(client: TestClient, session: Session):
    user1, credentials1 = generate_user(session, status=UserStatus.ACTIVE)
    user2, credentials2 = generate_user(session, status=UserStatus.ACTIVE)

    # User 1 logs and posts
    payload = {
        "content": "This forum is so cool!"
    }
    login_response = client.post(Endpoints.LOGIN.value, data=asdict(credentials1))
    assert login_response.status_code == 200, login_response.text
    access_token = login_response.json()["access_token"]
    post_response = client.post(Endpoints.NEW_POST.value, json=payload, headers={"Authorization": f"Bearer {access_token}"})
    assert post_response.status_code == 201

    # User 2 logs and likes user 1 post
    login_response = client.post(Endpoints.LOGIN.value, data=asdict(credentials2))
    assert login_response.status_code == 200, login_response.text
    access_token = login_response.json()["access_token"]
    post_id = session.exec(select(Post)).first().id

    endpoint = Endpoints.LIKE_POST.value.format(post_id)
    like_response = client.post(endpoint, headers={"Authorization": f"Bearer {access_token}"})
    assert like_response.status_code == 204

    # Check that the like exists
    likes_db = session.exec(select(Like)).all()
    like = likes_db[0]

    assert len(likes_db) == 1
    assert like.user_id == user2.id
    assert like.post_id == post_id


def test_user_cannot_like_its_own_post(client: TestClient, session: Session):
    user, credentials = generate_user(session, status=UserStatus.ACTIVE)

    payload = {
        "content": "THIS IS WORKING!!"
    }

    login_response = client.post(Endpoints.LOGIN.value, data=asdict(credentials))
    assert login_response.status_code == 200, login_response.text

    access_token = login_response.json()["access_token"]
    post_response = client.post(Endpoints.NEW_POST.value, json=payload, headers={"Authorization": f"Bearer {access_token}"})
    assert post_response.status_code == 201

    posts_db = session.exec(select(Post)).all()
    post = posts_db[0]

    endpoint = Endpoints.LIKE_POST.value.format(post.id)
    like_response = client.post(endpoint, headers={"Authorization": f"Bearer {access_token}"})
    assert like_response.status_code == 403, like_response.text