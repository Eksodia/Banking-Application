from fastapi import HTTPException
from sqlalchemy.orm import Session
from src.models.user import User
from src.schemas.user import UserCreate, UserUpdate
from uuid import UUID
from passlib.context import CryptContext
from src.models.user import UserRole

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserServices:
    def __init__(self):
        pass


    def get_all_users(self, db: Session, authenticated_user: User):
        if authenticated_user.role == UserRole.CLIENT:
            raise HTTPException(status_code=403, detail="Access denied")
        
        query = db.query(User)
        if authenticated_user.role == UserRole.BANKER:
            query = query.filter(User.role != UserRole.ADMIN)
        
        return query.all()


    def get_user(self, db: Session, user_id: UUID, authenticated_user: User):
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        if authenticated_user.role == UserRole.CLIENT and authenticated_user.id != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        if authenticated_user.role == UserRole.BANKER and user.role == UserRole.ADMIN:
            raise HTTPException(status_code=403, detail="Access denied")
        
        return user


    def get_user_by_email(self, db: Session, email: str):
        return db.query(User).filter(User.email == email).first()


    def create_user(self, db: Session, user: UserCreate, authenticated_user: User):
        if authenticated_user.role == UserRole.ADMIN and user.role == UserRole.CLIENT:
            raise HTTPException(status_code=403, detail="Admin can only create BANKER users")
        elif authenticated_user.role == UserRole.BANKER and user.role != UserRole.CLIENT:
            raise HTTPException(status_code=403, detail="Banker can only create CLIENT users")
        elif authenticated_user.role == UserRole.CLIENT:
            raise HTTPException(status_code=403, detail="Access denied")

        hashed_password = pwd_context.hash(user.password)
        db_user = User(
            username=user.username,
            email=user.email,
            hashed_password=hashed_password,
            role=user.role,
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user


    def update_user_service(self, user_id: UUID, user_update: UserUpdate, db: Session, authenticated_user: User):
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if authenticated_user.role == UserRole.CLIENT and authenticated_user.id != user_id:
            raise HTTPException(status_code=403, detail="Clients can only update themselves")
        
        if authenticated_user.role == UserRole.ADMIN and user == UserRole.CLIENT:
            raise HTTPException(status_code=403, detail="Admin can only update BANKER users")

        if authenticated_user.role == UserRole.BANKER and user.role != UserRole.CLIENT:
            raise HTTPException(status_code=403, detail="Banker can only update CLIENT users")

        if user_update.username:
            user.username = user_update.username
        if user_update.email:
            user.email = user_update.email
        if user_update.password:
            user.hashed_password = pwd_context.hash(user_update.password)
        if user_update.role and authenticated_user.role == UserRole.ADMIN:
            user.role = user_update.role

        db.commit()
        db.refresh(user)
        return user

    def delete_user_service(self, user_id: UUID, db: Session, authenticated_user: User):
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if authenticated_user.role == UserRole.ADMIN and user.role == UserRole.CLIENT:
            raise HTTPException(status_code=403, detail="Admin can only delete BANKER users")
        if authenticated_user.role == UserRole.BANKER and user.role != UserRole.CLIENT:
            raise HTTPException(status_code=403, detail="Banker can only delete CLIENT users")
        if authenticated_user.role == UserRole.CLIENT:
            raise HTTPException(status_code=403, detail="Clients cannot delete users")

        db.delete(user)
        db.commit()
        return {"detail": f"User {user_id} deleted"}