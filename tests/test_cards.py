import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.database import get_db, Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models.card import DebitCard
from src.models.user import User
from src.models.account import BankAccount, AccountStatus, AccountType
from src.services.auth_services import create_access_token, get_password_hash
from uuid import uuid4

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base.metadata.create_all(bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

@pytest.fixture(scope="module")
def banker_user():
    db = next(override_get_db())
    user = User(
        username="bankeruser2",
        email="banker2@example.com",
        hashed_password=get_password_hash("test"),
        role="BANKER"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    token = create_access_token({"sub": user.username})
    return token

@pytest.fixture(scope="module")
def created_card_id():
    db = next(override_get_db())
    card = DebitCard(
        id=uuid4(),
        account_id=uuid4(),
        monthly_salary = 1000,
        status="PENDING",
        decline_reason = None,
    )
    db.add(card)
    db.commit()
    return str(card.id)

@pytest.fixture(scope="module")
def client_user():
    db = next(override_get_db())
    user = User(
        username="clientuser1",
        email="client1@example.com",
        hashed_password=get_password_hash("test"),
        role="CLIENT"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    token = create_access_token({"sub": user.username})
    return token, user

@pytest.fixture(scope="module")
def client_account(client_user):
    _, user = client_user
    db = next(override_get_db())
    account = BankAccount(
        id=uuid4(),
        iban="DE44500105175407324931",
        type=AccountType.CURRENT,
        status=AccountStatus.ACTIVE,
        owner_id=user.id
    )
    db.add(account)
    db.commit()
    db.refresh(account)
    return account

@pytest.fixture(scope="module")
def client2_user():
    db = next(override_get_db())
    user = User(
        username="clientuser2",
        email="client2@example.com",
        hashed_password=get_password_hash("test"),
        role="CLIENT"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    token = create_access_token({"sub": user.username})
    return token, user

@pytest.fixture(scope="module")
def client2_account(client2_user):
    _, user = client2_user
    db = next(override_get_db())
    account = BankAccount(
        id=uuid4(),
        iban="FR44500105175407324941",
        type=AccountType.CURRENT,
        status=AccountStatus.ACTIVE,
        owner_id=user.id
    )
    db.add(account)
    db.commit()
    db.refresh(account)
    return account

def test_request_new_card(client_user, client_account):
    token, _ = client_user
    payload = {
        "account_id": str(client_account.id),
        "monthly_salary": 1000
    }
    response = client.post(
        "/card/",
        headers={"Authorization": f"Bearer {token}"},
        json=payload
    )
    assert response.status_code == 201
    assert response.json()["status"] == "PENDING"
    global created_card_id
    created_card_id = response.json()["id"]

def test_request_card_low_salary(client2_user, client2_account):
    token, _ = client2_user
    payload = {
        "account_id": str(client2_account.id),
        "monthly_salary": 100
    }
    response = client.post(
        "/card/",
        headers={"Authorization": f"Bearer {token}"},
        json=payload
    )
    assert response.status_code == 400
    assert "monthly salary must be at least" in response.json()["detail"]

def test_review_card_approve(banker_user, created_card_id):
    token = banker_user
    payload = {
        "status": "APPROVED"
    }
    response = client.patch(
        f"/card/{created_card_id}/approve",
        headers={"Authorization": f"Bearer {token}"},
        json=payload
    )
    print(response)
    assert response.status_code == 200
    assert response.json()["status"] == "APPROVED"

def test_get_all_cards(banker_user):
    token = banker_user
    response = client.get(
        "/card/",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_card_by_id(banker_user):
    token = banker_user
    response = client.get(
        f"/card/{created_card_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["id"] == created_card_id

def test_delete_card(banker_user):
    token = banker_user
    response = client.delete(
        f"/card/{created_card_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert "deleted" in response.json()["message"]
