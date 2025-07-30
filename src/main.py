from fastapi import FastAPI, Depends
import os
from src import router
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from sqlalchemy import text
from src.database import get_db  

load_dotenv()

app = FastAPI()

# Include routers
app.include_router(router.api_router)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

@app.get("/")
def get_homepage():
    return {"Response": "This is the home page"}


@app.get("/test-db")
def test_db_connection(db: Session = Depends(get_db)):
    try:
        result = db.execute(text("SELECT 1")).scalar()
        return {"success": True, "result": result}
    except Exception as e:
        return {"success": False, "error": str(e)}
