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


def test_users_crud_and_duplicate_email(client: TestClient) -> None:
    payload = {
        "name": "Ana Perez",
        "email": "ana@example.com",
        "role": "user",
        "is_active": True,
    }

    created = client.post("/users", json=payload)
    assert created.status_code == 201
    user_id = created.json()["id"]

    assert client.get("/users").json()["total"] == 1
    assert client.get(f"/users/{user_id}").status_code == 200
    assert client.put(
        f"/users/{user_id}",
        json={**payload, "name": "Ana Actualizada", "role": "support"},
    ).status_code == 200
    assert client.patch(f"/users/{user_id}", json={"is_active": False}).status_code == 200
    assert client.post("/users", json=payload).status_code == 400
    assert client.delete(f"/users/{user_id}").status_code == 204
    assert client.get(f"/users/{user_id}").status_code == 404


def test_invalid_payload_and_empty_patch(client: TestClient) -> None:
    invalid = client.post(
        "/users",
        json={"name": "A", "email": "not-an-email", "role": "invalid"},
    )
    assert invalid.status_code == 422

    created = client.post(
        "/users",
        json={
            "name": "Valid User",
            "email": "valid@example.com",
            "role": "user",
            "is_active": True,
        },
    )
    user_id = created.json()["id"]
    assert client.patch(f"/users/{user_id}", json={}).status_code == 400
