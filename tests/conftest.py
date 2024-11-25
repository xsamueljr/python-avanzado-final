from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient
from sqlmodel import create_engine, SQLModel, Session
from sqlmodel.pool import StaticPool

from main import app
from dependencies import get_session
from email_manager import EmailManager


@pytest.fixture()
def session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture()
def client(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()


@pytest.fixture()
def mock_email_manager(monkeypatch: pytest.MonkeyPatch) -> Mock:
    """
    The fixture returns a mock representing 
    the `EmailManager.send_confirmation_link` method, so 
    you can assert if it was called
    """
    mock = Mock()

    # Mock the init too, so it doesn't start an SMTP server
    monkeypatch.setattr(EmailManager, "__init__", lambda self: None)
    monkeypatch.setattr(EmailManager, "send_confirmation_link", mock)
    return mock
