from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from src.services.auth_services import get_current_user
from src.database import get_db
from src.models.user import User
from src.schemas.transaction import TransactionCreate, TransactionOut
from src.services.transaction_services import TransactionService

router = APIRouter()

transaction_service = TransactionService()


@router.get("/", response_model=List[TransactionOut])
def get_all_transactions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return transaction_service.get_transactions(db, current_user)


@router.get("/{transaction_id}", response_model=TransactionOut)
def get_transaction_by_id(
    transaction_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return transaction_service.get_transaction_by_id(db, transaction_id, current_user)


@router.post("/{account_id}", response_model=TransactionOut)
def create_transaction(
    account_id: UUID,
    transaction_data: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return transaction_service.perform_transaction(db, account_id, transaction_data, current_user)


@router.delete("/{transaction_id}")
def delete_transaction(
    transaction_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return transaction_service.delete_transaction(db, transaction_id, current_user)