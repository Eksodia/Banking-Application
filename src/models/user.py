from sqlalchemy import Column, String, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from src.database import Base
import enum, uuid

class UserRole(str, enum.Enum):
    ADMIN = "ADMIN"
    BANKER = "BANKER"
    CLIENT = "CLIENT"

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.CLIENT, nullable=False)

    accounts = relationship("BankAccount", back_populates="owner")