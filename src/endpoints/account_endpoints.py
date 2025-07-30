from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy.orm import Session
from src.database import get_db
from src.services.auth_services import get_current_user
from src.models.user import User
from src.models.account import AccountStatus
from src.schemas.account import AccountCreate, AccountUpdate, AccountOut
from src.services.account_services import AccountServices
from uuid import UUID

router = APIRouter()
account_services = AccountServices()

@router.post("/admin-create", response_model=AccountOut)
def create_account(
    owner_id: UUID, 
    account: AccountCreate = Body(...), 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "ADMIN":
        raise HTTPException(
            status_code=403,
            detail="Only admins can create accounts"
        )
    return account_services.create_account(db, owner_id, account)


@router.post("/")
def request_new_account(
    owner_id: UUID, 
    account: AccountCreate = Body(...), 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)):
    return account_services.request_new_account(db, owner_id, account, current_user)


@router.get("/{account_id}", response_model=AccountOut)
def get_account(
    account_id: UUID, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return account_services.get_account(db, account_id, current_user)


@router.get("/", response_model=list[AccountOut])
def get_all_accounts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return account_services.get_all_accounts(db, current_user)


@router.patch("/{account_id}", response_model=AccountOut)
def update_account(
    account_id: UUID, 
    account_update: AccountUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return account_services.update_account(db, account_id, account_update, current_user)


@router.patch("/{account_id}/activate", response_model=AccountOut)
def activate_account(
    account_id: UUID, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return account_services.update_status(db, account_id, current_user, status=AccountStatus.ACTIVE)


@router.patch("/{account_id}/decline", response_model=AccountOut)
def decline_account(
    account_id: UUID, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return account_services.update_status(db, account_id, current_user, status=AccountStatus.DECLINED)


@router.delete("/{account_id}")
def delete_account(
    account_id: UUID, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return account_services.delete_account(db, account_id, current_user)