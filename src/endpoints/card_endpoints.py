from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from src.database import get_db
from src.services.auth_services import get_current_user
from src.models.user import User
from src.models.card import CardStatus
from src.schemas.card import CardCreate, CardOut
from src.services.card_services import CardServices
from uuid import UUID

router = APIRouter()
card_services = CardServices()

@router.post("/", response_model=CardOut, status_code=status.HTTP_201_CREATED)
def request_new_card(
    card: CardCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return card_services.create_card_request(db, card, current_user)


@router.patch("/{card_id}/approve", response_model=CardOut)
def approve_card(
    card_id: UUID, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    return card_services.update_status(db, card_id, CardStatus.APPROVED , current_user)


@router.patch("/{card_id}/decline", response_model=CardOut)
def decline_card(
    card_id: UUID, 
    reason: str,
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    return card_services.update_status(db, card_id, CardStatus.DECLINED , current_user, reason)


@router.get("/", response_model=list[CardOut])
def get_all_cards(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return card_services.get_cards(db, current_user)


@router.get("/{card_id}", response_model=CardOut)
def get_card_by_id(
    card_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return card_services.get_card_by_id(db, card_id, current_user)

@router.delete("/{card_id}")
def delete_card(
    card_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return card_services.delete_card(db, card_id, current_user)
