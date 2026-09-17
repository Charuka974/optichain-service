from datetime import datetime, timezone
from bson import ObjectId

def format_user(user: dict) -> dict:
    """
    Format a MongoDB user document into a standardized dictionary.
    """
    if not user:
        return None
    return {
        "id": str(user.get("_id")),
        "email": user.get("email"),
        "hashed_password": user.get("hashed_password"),
        "role": user.get("role", "analyst"),
        "created_at": user.get("created_at")
    }

def format_prediction_record(record: dict) -> dict:
    """
    Format a MongoDB prediction record document into a standardized dictionary matching SQL output structure.
    """
    if not record:
        return None
    
    created_at = record.get("created_at")
    if isinstance(created_at, datetime):
        created_at_str = created_at.isoformat()
    else:
        created_at_str = str(created_at) if created_at else datetime.now(timezone.utc).isoformat()

    return {
        "id": str(record.get("_id")),
        "user_id": record.get("user_id"),
        "input_data": record.get("input_data"),
        "delayed": record.get("delayed"),
        "delay_probability": record.get("delay_probability"),
        "created_at": created_at_str
    }