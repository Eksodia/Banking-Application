import uuid
from sqlalchemy import UUID, Column, Float, String, ForeignKey, Enum
from sqlalchemy.orm import relationship
from src.database import Base
import enum

class TransactionType(str, enum.Enum):
    DEBIT = "DEBIT"
    CREDIT = "CREDIT"

class Currency(str, enum.Enum):
    EURO = "EUR"
    DOLLAR = "USD"
    LEK = "ALL"

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id"))
    amount = Column(Float, nullable=False)
    currency = Column(String, default=Currency.EURO)
    type = Column(Enum(TransactionType), nullable=False)
    description = Column(String, nullable=True)

    account = relationship("BankAccount", back_populates="transactions")