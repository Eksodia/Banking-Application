from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.services.auth_services import get_current_user
from src.models.user import User
from src.schemas.user import UserCreate, UserOut, UserUpdate
from src.services.user_services import UserServices
from src.database import get_db

router = APIRouter()
user_services = UserServices()

@router.post("/", response_model=UserOut)
def create_user(
    user: UserCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_user = user_services.get_user_by_email(db, user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return user_services.create_user(db, user, current_user)


@router.get("/", response_model=list[UserOut])
def get_all_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return user_services.get_all_users(db, current_user)


@router.get("/{user_id}", response_model=UserOut)
def api_get_user(
    user_id: UUID, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_user = user_services.get_user(db, user_id, current_user)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@router.patch("/{user_id}", response_model=UserOut)
def update_user(
    user_id: UUID, 
    user_update: UserUpdate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return user_services.update_user_service(user_id, user_update, db, current_user)


@router.delete("/{user_id}")
def delete_user(
    user_id: UUID, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return user_services.delete_user_service(user_id, db, current_user)