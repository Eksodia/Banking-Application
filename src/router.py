from fastapi import APIRouter
from src.endpoints import user_endpoints, account_endpoints, card_endpoints, transaction_endpoints, auth_endpoints

api_router = APIRouter()

api_router.include_router(user_endpoints.router, prefix="/users", tags=["USERS"])
api_router.include_router(account_endpoints.router, prefix="/account", tags=["ACCOUNT"])
api_router.include_router(card_endpoints.router, prefix="/card", tags=["CARD"])
api_router.include_router(transaction_endpoints.router, prefix="/transaction", tags=["TRANSACTION"])
api_router.include_router(auth_endpoints.router, prefix="/login", tags=["LOGIN"])
