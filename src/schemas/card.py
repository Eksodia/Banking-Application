from pydantic import BaseModel, ConfigDict
from src.models.card import CardStatus
from typing import Optional
from uuid import UUID


class CardBase(BaseModel):
    monthly_salary: float
    account_id: UUID

class CardCreate(CardBase):
    pass

class CardOut(CardBase):
    id: UUID
    status: CardStatus
    decline_reason: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class CardReview(BaseModel):
    status: CardStatus
    decline_reason: Optional[str] = None
