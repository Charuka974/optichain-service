from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from pymongo.database import Database
from pymongo.errors import DuplicateKeyError
from app.db.session import get_db
from app.schemas.payload import UserRegister, UserLogin
from app.core.security import hash_password, verify_password, create_access_token

router = APIRouter()

@router.post("/register")
def register(user_data: UserRegister, db: Database = Depends(get_db)):
    if db["users"].find_one({"email": user_data.email}):
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user_doc = {
        "email": user_data.email,
        "hashed_password": hash_password(user_data.password),
        "role": user_data.role,
        "created_at": datetime.now(timezone.utc)
    }
    
    try:
        db["users"].insert_one(user_doc)
    except DuplicateKeyError:
        raise HTTPException(status_code=400, detail="Email already registered")
        
    return {"message": "User registered successfully"}

@router.post("/login")
def login(credentials: UserLogin, db: Database = Depends(get_db)):
    user = db["users"].find_one({"email": credentials.email})
    if not user or not verify_password(credentials.password, user.get("hashed_password", "")):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    user_id_str = str(user["_id"])
    role = user.get("role", "analyst")
    token = create_access_token({"sub": user_id_str, "email": user["email"], "role": role})
    return {"access_token": token, "token_type": "bearer", "role": role}