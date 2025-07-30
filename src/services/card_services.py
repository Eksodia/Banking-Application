from uuid import UUID
from sqlalchemy.orm import Session
from src.models.card import DebitCard, CardStatus
from src.models.account import BankAccount, AccountStatus, AccountType
from src.schemas.card import CardCreate
from fastapi import HTTPException
from src.models.user import User, UserRole

class CardServices():
    def __init__(self):
        pass


    def create_card_request(self, db: Session, card_data: CardCreate, authenticated_user: User):
        if card_data.monthly_salary < 500:
            raise HTTPException(
                status_code=400,
                detail="Cannot apply for debit card: monthly salary must be at least 500€."
            )
        
        account = db.query(BankAccount).filter(BankAccount.id == card_data.account_id).first()

        if not account:
            raise HTTPException(status_code=404, detail="Account not found")

        if account.status != AccountStatus.ACTIVE or account.type != AccountType.CURRENT:
            raise HTTPException(status_code=400, detail="Account must be an active current account")
        
        if authenticated_user.role != UserRole.CLIENT:
            raise HTTPException(status_code=403, detail="Only client can request a new card")
        
        existing_card = db.query(DebitCard).filter(DebitCard.account_id == card_data.account_id).first()

        if existing_card:
            raise HTTPException(status_code=400, detail=f"A debit card has already been issued for this account")

        new_card = DebitCard(
            monthly_salary=card_data.monthly_salary,
            account_id=card_data.account_id,
            status=CardStatus.PENDING
        )

        db.add(new_card)
        db.commit()
        db.refresh(new_card)
        return new_card

    
    def update_status(self, db: Session, card_id: UUID, status: CardStatus, authenticated_user: User, decline_reason: str = None):
        if authenticated_user.role != UserRole.BANKER:
            raise HTTPException(status_code=403, detail="Only banker can review card")
        
        card = db.query(DebitCard).filter(DebitCard.id == card_id).first()

        if not card:
            raise HTTPException(status_code=404, detail="Card not found")
        
        if card.status != CardStatus.PENDING:
            raise HTTPException(status_code=400, detail="Card has already been reviewed")

        if status == CardStatus.DECLINED and not decline_reason:
            raise HTTPException(status_code=400, detail="Decline reason must be provided")

        card.status = status
        card.decline_reason = decline_reason if status == CardStatus.DECLINED else None

        db.commit()
        db.refresh(card)
        return card
    


    def delete_card(self, db: Session, card_id: UUID, authenticated_user: User):
        if authenticated_user.role == UserRole.CLIENT:
            raise HTTPException(status_code=403, detail="Only admin or banker can delete card applications")

        card = db.query(DebitCard).filter(DebitCard.id == card_id).first()
        if not card:
            raise HTTPException(status_code=404, detail="Card not found")

        db.delete(card)
        db.commit()
        return {"message": "Card deleted successfully"}
        

    def get_cards(self, db: Session, authenticated_user: User):
        if authenticated_user.role != UserRole.CLIENT:
            return db.query(DebitCard).all()
        raise HTTPException(status_code=403, detail="Not authorized to view all cards")


    def get_card_by_id(self, db: Session, card_id: UUID, authenticated_user: User) -> DebitCard:
        card = db.query(DebitCard).filter(DebitCard.id == card_id).first()
        if not card:
            raise HTTPException(status_code=404, detail="Card not found")

        account = db.query(BankAccount).filter(BankAccount.id == card.account_id).first()
        if authenticated_user.role == UserRole.CLIENT and account.owner_id != authenticated_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to view this card")

        return card