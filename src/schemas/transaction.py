from pydantic import BaseModel, UUID4, ConfigDict

class TransactionCreate(BaseModel):
    recipient_iban: str
    amount: float

class TransactionOut(BaseModel):
    id: UUID4
    account_id: UUID4
    amount: float
    currency: str
    type: str

    model_config = ConfigDict(from_attributes=True)
