from pydantic import BaseModel, ConfigDict
from typing import Optional
from uuid import UUID
from src.models.account import AccountStatus, AccountType


class AccountCreate(BaseModel):
    currency: Optional[str] = "EUR"
    type: AccountType

class AccountUpdate(BaseModel):
    balance: Optional[float] = None
    status: Optional[AccountStatus] = None
    type: Optional[AccountType] = None

class AccountOut(BaseModel):
    id: UUID
    iban: str
    balance: float
    currency: str
    status: AccountStatus
    type: AccountType
    owner_id: UUID

    model_config = ConfigDict(from_attributes=True)
