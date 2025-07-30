import pytest
from fastapi.testclient import TestClient
from sqlalchemy import UUID, create_engine
from sqlalchemy.orm import sessionmaker
from uuid import uuid4

from src.main import app
from src.database import get_db, Base
from src.models.user import User
from src.models.account import BankAccount, AccountType, AccountStatus
from src.services.auth_services import get_password_hash, create_access_token

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
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
def client_user():
    db = next(override_get_db())
    user = User(
        username="transaction_client",
        email="tclient@example.com",
        hashed_password=get_password_hash("password"),
        role="CLIENT"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    token = create_access_token({"sub": user.username})
    return token, user

@pytest.fixture(scope="module")
def banker_user():
    db = next(override_get_db())
    user = User(
        username="transaction_banker",
        email="tbanker@example.com",
        hashed_password=get_password_hash("password"),
        role="BANKER"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    token = create_access_token({"sub": user.username})
    return token

@pytest.fixture(scope="module")
def sender_account(client_user):
    db = next(override_get_db())
    _, user = client_user
    account = BankAccount(
        id=uuid4(),
        iban="AL93202111090000000001234567",
        balance=1000.0,
        currency="EUR",
        status=AccountStatus.ACTIVE,
        type=AccountType.CURRENT,
        owner_id=user.id
    )
    db.add(account)
    db.commit()
    db.refresh(account)
    return account

@pytest.fixture(scope="module")
def recipient_account(client_user):
    db = next(override_get_db())
    _, user = client_user
    account = BankAccount(
        id=uuid4(),
        iban="AL47212110090000000235698741",
        balance=500.0,
        currency="EUR",
        status=AccountStatus.ACTIVE,
        type=AccountType.CURRENT,
        owner_id=user.id
    )
    db.add(account)
    db.commit()
    db.refresh(account)
    return account

def test_create_transaction(client_user, sender_account, recipient_account):
    db = next(override_get_db())
    token, _ = client_user
    from src.models.card import DebitCard
    card = DebitCard(monthly_salary=2000, account_id=sender_account.id, status="APPROVED")
    db.add(card)
    db.commit()

    payload = {
        "recipient_iban": recipient_account.iban,
        "amount": 200.0
    }

    response = client.post(
        f"/transaction/{sender_account.id}",
        headers={"Authorization": f"Bearer {token}"},
        json=payload
    )
    assert response.status_code == 200
    tx = response.json()
    assert tx["amount"] == 200.0
    assert tx["type"] == "DEBIT"
    assert tx["currency"] == "EUR"
    global created_transaction_id
    created_transaction_id = tx["id"]

def test_get_all_transactions(banker_user, sender_account):
    token = banker_user
    response = client.get(
        "/transaction/",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    txs = response.json()
    assert isinstance(txs, list)
    assert any(tx["account_id"] == str(sender_account.id) for tx in txs)

def test_get_transaction_by_id(client_user):
    token, _ = client_user
    response = client.get(
        f"/transaction/{created_transaction_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    tx = response.json()
    assert tx["id"] == created_transaction_id

def test_client_cannot_delete_transaction(client_user):
    token, _ = client_user
    response = client.delete(
        f"/transaction/{created_transaction_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 403
    assert "cannot delete transactions" in response.json()["detail"]

def test_banker_can_delete_transaction(banker_user):
    token = banker_user
    response = client.delete(
        f"/transaction/{created_transaction_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert "deleted successfully" in response.json()["detail"]
