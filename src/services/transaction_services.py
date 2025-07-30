from fastapi import HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from src.models.account import BankAccount
from src.models.transaction import Transaction, TransactionType
from src.schemas.transaction import TransactionCreate
from src.models.user import User, UserRole


class TransactionService:
    def __init__(self):
        pass


    def get_transactions(self, db: Session, authenticated_user: User):
        if authenticated_user.role == UserRole.CLIENT:
            accounts = db.query(BankAccount).filter(BankAccount.owner_id == authenticated_user.id).all()
            account_ids = [acc.id for acc in accounts]
            return db.query(Transaction).filter(Transaction.account_id.in_(account_ids)).all()

        return db.query(Transaction).all()
    

    def get_transaction_by_id(self, db: Session, tx_id: UUID, authenticated_user: User):
        tx = db.query(Transaction).filter(Transaction.id == tx_id).first()
        if not tx:
            raise HTTPException(status_code=404, detail="Transaction not found")

        if authenticated_user.role == UserRole.CLIENT:
            account = db.query(BankAccount).filter(BankAccount.id == tx.account_id).first()
            if account.owner_id != authenticated_user.id:
                raise HTTPException(status_code=403, detail="Access denied to this transaction")

        return tx


    def perform_transaction(self, db: Session, sender_account_id: UUID, data: TransactionCreate, authenticated_user: User):
        sender_account = db.query(BankAccount).filter(BankAccount.id == sender_account_id).first()
        if not sender_account:
            raise HTTPException(status_code=404, detail="Sender account not found")


        if authenticated_user.role == UserRole.CLIENT and sender_account.owner_id != authenticated_user.id:
            raise HTTPException(status_code=403, detail="You don't have permission to perform this transaction")

        
        if not sender_account.card:
            raise HTTPException(status_code=400, detail="No linked debit card on sender account")

        
        if sender_account.balance < data.amount:
            raise HTTPException(status_code=400, detail="Insufficient funds")

        
        recipient_account = db.query(BankAccount).filter(BankAccount.iban == data.recipient_iban).first()
        if not recipient_account:
            raise HTTPException(status_code=404, detail="Recipient account not found")

        
        debit_tx = Transaction(
            account_id=sender_account.id,
            amount=data.amount,
            currency=sender_account.currency,
            type=TransactionType.DEBIT
        )
        sender_account.balance -= data.amount

        
        credit_tx = Transaction(
            account_id=recipient_account.id,
            amount=data.amount,
            currency=recipient_account.currency,
            type=TransactionType.CREDIT
        )
        recipient_account.balance += data.amount

        db.add(debit_tx)
        db.add(credit_tx)
        db.commit()
        db.refresh(debit_tx)

        return debit_tx
    

    def delete_transaction(self, db: Session, tx_id: UUID, authenticated_user: User):
        tx = db.query(Transaction).filter(Transaction.id == tx_id).first()
        if not tx:
            raise HTTPException(status_code=404, detail="Transaction not found")

        if authenticated_user.role == UserRole.CLIENT:
            raise HTTPException(status_code=403, detail="Clients cannot delete transactions")


        db.delete(tx)
        db.commit()
        return {"detail": "Transaction deleted successfully"}
