import json
from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from pymongo.database import Database
from app.schemas.payload import SupplyChainInput, PredictionResponse
from app.ml.inference import ml_service
from app.db.session import get_db
from app.db.models import format_prediction_record
from app.api.dependencies import authenticate

router = APIRouter()

@router.post("/predict", response_model=PredictionResponse)
async def predict_delay(payload: SupplyChainInput, db: Database = Depends(get_db), user: dict = Depends(authenticate)):
    # 1. Extract raw dictionary with the exact aliases (keys with spaces)
    input_dict = payload.model_dump(by_alias=True)
    
    # 2. Run Inference
    result = ml_service.predict(input_dict)
    
    # 3. Save Prediction to MongoDB
    record_doc = {
        "user_id": user.get("user_id"),
        "input_data": json.dumps(input_dict),
        "delayed": result["delayed"],
        "delay_probability": result["delay_probability"],
        "created_at": datetime.now(timezone.utc)
    }
    db["prediction_records"].insert_one(record_doc)
    
    return result

@router.get("/predictions/history")
def get_prediction_history(db: Database = Depends(get_db)):
    cursor = db["prediction_records"].find().sort("created_at", -1).limit(20)
    records = [format_prediction_record(doc) for doc in cursor]
    return records