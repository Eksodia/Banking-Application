import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
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
def test_token():
    db = next(override_get_db())
    hashed_password = get_password_hash("testpass")
    user = User(
        username="testuser",
        email="admin@example.com",
        hashed_password=hashed_password,
        role="ADMIN"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    token = create_access_token({"sub": user.username})
    return token


def test_get_all_users(test_token):
    response = client.get(
        "/users/",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_create_user(test_token):
    payload = {
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "newpass",
        "role": "BANKER"
    }
    response = client.post(
        "/users/",
        headers={"Authorization": f"Bearer {test_token}"},
        json=payload
    )
    assert response.status_code == 200
    assert response.json()["email"] == payload["email"]


def test_update_user(test_token):
    create_payload = {
        "username": "updateuser",
        "email": "updateuser@example.com",
        "password": "oldpass",
        "role": "BANKER"
    }
    create_response = client.post(
        "/users/",
        headers={"Authorization": f"Bearer {test_token}"},
        json=create_payload
    )
    assert create_response.status_code == 200
    user_id = create_response.json()["id"] 

    update_payload = {
        "email": "updatedemail@example.com",
        "password": "newpass"
    }

    response = client.patch(
        f"/users/{user_id}",
        headers={"Authorization": f"Bearer {test_token}"},
        json=update_payload
    )
    assert response.status_code == 200
    json_resp = response.json()
    assert json_resp["email"] == update_payload["email"]

def test_delete_user(test_token):
    create_payload = {
        "username": "deleteuser",
        "email": "deleteuser@example.com",
        "password": "somepass",
        "role": "BANKER"
    }
    create_response = client.post(
        "/users/",
        headers={"Authorization": f"Bearer {test_token}"},
        json=create_payload
    )
    assert create_response.status_code == 200
    user_id = create_response.json()["id"]


    delete_response = client.delete(
        f"/users/{user_id}",
        headers={"Authorization": f"Bearer {test_token}"},
    )
    assert delete_response.status_code == 200


    get_response = client.get(
        f"/users/{user_id}",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert get_response.status_code == 404
