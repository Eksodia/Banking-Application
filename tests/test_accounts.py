import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from uuid import uuid4
from src.database import Base, get_db
from src.main import app
from src.models.user import User
from src.services.auth_services import create_access_token, get_password_hash
import os


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
db_path = os.path.join(BASE_DIR, "test.db")
SQLALCHEMY_DATABASE_URL = f"sqlite:///{db_path}"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
Base.metadata.create_all(bind=engine)
client = TestClient(app)

@pytest.fixture(scope="module")
def test_client_token():
    db = next(override_get_db())
    hashed_password = get_password_hash("clientpass")
    user = User(
        username="clientuser",
        email="client@example.com",
        hashed_password=hashed_password,
        role="CLIENT"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    token = create_access_token({"sub": user.username})
    return token, str(user.id)


@pytest.fixture(scope="module")
def test_banker_token():
    db = next(override_get_db())
    hashed_password = get_password_hash("bankerpass")
    user = User(
        username="bankeruser",
        email="banker@example.com",
        hashed_password=hashed_password,
        role="BANKER"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    token = create_access_token({"sub": user.username})
    return token


@pytest.fixture(scope="module")
def created_account_id_fixture(test_client_token):
    token, user_id = test_client_token
    payload = {
        "currency": "EUR",
        "type": "CURRENT"
    }
    response = client.post(
        f"/account/?owner_id={user_id}",
        headers={"Authorization": f"Bearer {token}"},
        json=payload
    )
    assert response.status_code == 200
    return response.json()["id"]


def test_create_account(test_client_token):
    token, user_id = test_client_token
    payload = {
        "currency": "EUR",
        "type": "CURRENT"
    }
    response = client.post(
        f"/account/?owner_id={user_id}",
        headers={"Authorization": f"Bearer {token}"},
        json=payload
    )
    assert response.status_code == 200
    data = response.json()
    assert data["currency"] == "EUR"
    assert data["type"] == "CURRENT"
    assert data["status"] == "PENDING"


def test_get_account(test_client_token, created_account_id_fixture):
    token, _ = test_client_token
    response = client.get(
        f"/account/{created_account_id_fixture}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["id"] == created_account_id_fixture


def test_get_all_accounts(test_banker_token):
    token = test_banker_token
    response = client.get(
        "/account/",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_update_account(test_banker_token, created_account_id_fixture):
    token = test_banker_token
    update_payload = {
        "balance": 1000,
        "status": "ACTIVE"
        
    }
    response = client.patch(
        f"/account/{created_account_id_fixture}",
        headers={"Authorization": f"Bearer {token}"},
        json=update_payload
    )
    print(response.status_code)
    print(response.json())

    assert response.status_code == 200
    assert response.json()["status"] == "ACTIVE"


def test_delete_account(test_banker_token, created_account_id_fixture):
    token = test_banker_token
    response = client.delete(
        f"/account/{created_account_id_fixture}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert "deleted" in response.json()["detail"]