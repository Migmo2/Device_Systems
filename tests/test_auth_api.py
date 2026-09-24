from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.database.connection import Base
from app.dependencies.database_dependency import database_session
from app.main import app


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(engine)

    def override_database_session() -> Generator[Session, None, None]:
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[database_session] = override_database_session
    yield TestClient(app)
    app.dependency_overrides.clear()
    Base.metadata.drop_all(engine)


def test_register_login_and_me_hides_password_hash(client: TestClient) -> None:
    payload = {
        "name": "Security User",
        "email": "security@example.com",
        "password": "SecurePass1",
        "role": "user",
    }
    registered = client.post("/auth/register", json=payload)
    assert registered.status_code == 201
    assert "hashed_password" not in registered.text

    login = client.post(
        "/auth/login",
        data={"username": payload["email"], "password": payload["password"]},
    )
    assert login.status_code == 200
    token = login.json()["access_token"]
    me = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert "hashed_password" not in me.text


def test_auth_errors_and_password_validation(client: TestClient) -> None:
    weak = client.post(
        "/auth/register",
        json={"name": "Weak User", "email": "weak@example.com", "password": "weakpass"},
    )
    assert weak.status_code == 422
    assert client.get("/auth/me").status_code == 401
    assert client.post(
        "/auth/login",
        data={"username": "missing@example.com", "password": "WrongPass1"},
    ).status_code == 401


def test_register_rate_limit(client: TestClient) -> None:
    for index in range(3):
        response = client.post(
            "/auth/register",
            json={
                "name": f"Rate User {index}",
                "email": f"rate{index}@example.com",
                "password": "RatePass1",
            },
        )
        assert response.status_code == 201

    limited = client.post(
        "/auth/register",
        json={
            "name": "Rate Limited",
            "email": "limited@example.com",
            "password": "RatePass1",
        },
    )
    assert limited.status_code == 429
