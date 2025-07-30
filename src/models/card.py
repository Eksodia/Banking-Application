import uuid
from sqlalchemy import UUID, Column, Float, String, ForeignKey, Enum
from sqlalchemy.orm import relationship
from src.database import Base
import enum

class CardStatus(str, enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    DECLINED = "DECLINED"

class DebitCard(Base):
    __tablename__ = "debit_cards"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    monthly_salary = Column(Float, nullable=False)
    status = Column(Enum(CardStatus), default=CardStatus.PENDING)
    decline_reason = Column(String, nullable=True)

    account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id"), unique=True)
    linked_account = relationship("BankAccount", back_populates="card")