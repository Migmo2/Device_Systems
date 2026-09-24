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


def test_device_loan_return_and_join_details(client: TestClient) -> None:
    user = client.post(
        "/users",
        json={
            "name": "Ana Perez",
            "email": "ana.loan@example.com",
            "role": "user",
            "is_active": True,
        },
    ).json()
    device = client.post(
        "/devices",
        json={
            "name": "Laptop ThinkPad",
            "serial_number": "LEN-TEST-001",
            "device_type": "laptop",
            "brand": "Lenovo",
            "is_available": True,
        },
    ).json()

    loan = client.post(
        "/loans", json={"user_id": user["id"], "device_id": device["id"]}
    )
    assert loan.status_code == 201
    loan_id = loan.json()["id"]

    assert client.post(
        "/loans", json={"user_id": user["id"], "device_id": device["id"]}
    ).status_code == 409
    details = client.get("/loans/details", params={"device_type": "laptop"})
    assert details.status_code == 200
    assert details.json()[0]["user"]["email"] == "ana.loan@example.com"
    assert client.get(f"/users/{user['id']}/loans").status_code == 200

    assert client.patch(f"/loans/{loan_id}/return").status_code == 200
    available = client.get("/devices", params={"is_available": True}).json()
    assert any(item["id"] == device["id"] for item in available)
    assert client.patch(f"/loans/{loan_id}/return").status_code == 409


def test_device_serial_is_unique(client: TestClient) -> None:
    payload = {
        "name": "Router Principal",
        "serial_number": "ROUTER-001",
        "device_type": "router",
        "brand": "Cisco",
        "is_available": True,
    }
    assert client.post("/devices", json=payload).status_code == 201
    assert client.post("/devices", json={**payload, "name": "Router Backup"}).status_code == 400
