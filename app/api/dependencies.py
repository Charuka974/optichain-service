from fastapi import Header, HTTPException, Depends
from app.db.session import get_db

async def authenticate(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized: Missing or invalid token")
    # In a full production app, you decode the JWT here
    return {"user_id": 1}