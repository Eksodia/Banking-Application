from sqlalchemy import Column, String, Float, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum
import uuid
from src.database import Base

class AccountStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    PENDING = "PENDING"
    DECLINED = "DECLINED"

class AccountType(str, enum.Enum):
    CURRENT = "CURRENT"
    SAVINGS = "SAVINGS"

class BankAccount(Base):
    __tablename__ = "accounts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    iban = Column(String, unique=True, nullable=False)
    balance = Column(Float, default=0.0)
    currency = Column(String, default="EUR")
    status = Column(Enum(AccountStatus), default=AccountStatus.PENDING.value)
    type = Column(Enum(AccountType), nullable=False)

    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    owner = relationship("User", back_populates="accounts")

    card = relationship("DebitCard", back_populates="linked_account", uselist=False)
    transactions = relationship("Transaction", back_populates="account", cascade="all, delete-orphan")
