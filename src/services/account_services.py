from fastapi import HTTPException
from sqlalchemy.orm import Session
from src.models import BankAccount
from src.schemas.account import AccountCreate, AccountUpdate
from uuid import UUID
import random, string
from src.models.user import User, UserRole
from src.models.account import AccountStatus

class AccountServices:
    def __init__(self):
        pass


    def create_account(self, db: Session, owner_id: UUID, account: AccountCreate, status = AccountStatus.ACTIVE.value) -> BankAccount:
        db_account = BankAccount(
            iban=self.generate_random_iban(),
            currency=account.currency,
            type=account.type,
            owner_id=owner_id,
            balance=0.0,
            status=status
        )
        db.add(db_account)
        db.commit()
        db.refresh(db_account)
        return db_account


    def request_new_account(self, db: Session, owner_id: UUID, account: AccountCreate, authenticated_user: User) -> BankAccount:
        if authenticated_user.role != UserRole.CLIENT:
            raise HTTPException(status_code=403, detail="Only clients can request new accounts")

        if authenticated_user.id != owner_id:
            raise HTTPException(status_code=403, detail="Clients can only create accounts for themselves")
        return self.create_account(db, owner_id, account, status = AccountStatus.PENDING)


    def get_account(self, db: Session, account_id: UUID, authenticated_user: User) -> BankAccount:
        acc = db.query(BankAccount).filter(BankAccount.id == account_id).first()
        if not acc:
            raise HTTPException(status_code=404, detail="Account not found")

        if authenticated_user.role == UserRole.CLIENT and acc.owner_id != authenticated_user.id:
            raise HTTPException(status_code=403, detail="Access denied")

        return acc

   
    def get_all_accounts(self, db: Session, authenticated_user: User):
        if authenticated_user.role == UserRole.CLIENT:
            raise HTTPException(status_code=403, detail="Access denied")
        return db.query(BankAccount).all()
    

    def update_account(self, db: Session, account_id: UUID, account_update: AccountUpdate, authenticated_user: User) -> BankAccount:
        account = db.query(BankAccount).filter(BankAccount.id == account_id).first()
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")

        if authenticated_user.role != UserRole.BANKER:
            raise HTTPException(status_code=403, detail="Only bankers can update account")

        for var, value in vars(account_update).items():
            if value is not None:
                setattr(account, var, value)

        db.commit()
        db.refresh(account)
        return account


    def update_status(self, db: Session, account_id: UUID, authenticated_user: User, status: AccountStatus) -> BankAccount:
        account = db.query(BankAccount).filter(BankAccount.id == account_id).first()
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")

        if authenticated_user.role != UserRole.BANKER:
            raise HTTPException(status_code=403, detail="Only bankers can update account")

        account.status = status

        db.commit()
        db.refresh(account)
        return account
    

    def delete_account(self, db: Session, account_id: UUID, authenticated_user: User):
        account = db.query(BankAccount).filter(BankAccount.id == account_id).first()
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")

        if authenticated_user.role == UserRole.CLIENT:
            raise HTTPException(status_code=403, detail="Only bankers or admins can delete accounts")

        db.delete(account)
        db.commit()
        return {"detail": f"Account {account_id} deleted"}


    def generate_random_iban(self):
        EURO_IBAN_FORMATS = {
                "DE": 22,  
                "FR": 27,  
                "ES": 24,  
                "IT": 27,  
                "NL": 18,  
        }
        country = random.choice(list(EURO_IBAN_FORMATS.keys()))
        iban_length = EURO_IBAN_FORMATS[country]

        bban_length = iban_length - 4
        bban = ''.join(random.choices(string.ascii_uppercase + string.digits, k=bban_length))
        temp_iban = country + '00' + bban

        def calculate_check_digits(iban_str):
            rearranged = iban_str[4:] + iban_str[:4]

            numeric_iban = ''.join(str(int(ch, 36)) if ch.isalpha() else ch for ch in rearranged)
            remainder = int(numeric_iban) % 97
            check_digits = 98 - remainder
            return f"{check_digits:02d}"

        check_digits = calculate_check_digits(temp_iban)
        return country + check_digits + bban