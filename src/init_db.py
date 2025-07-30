from src.database import Base, engine
from src.models import User, Transaction, BankAccount, DebitCard

print("Creating all tables...")
Base.metadata.create_all(bind=engine)
print("Tables created.")