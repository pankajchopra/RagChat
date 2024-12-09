from fastapi import APIRouter, HTTPException
from app.database import get_database
from app.models import Preferences

router = APIRouter()
db = get_database()


@router.get("/api/preferences/{user_id}")
async def get_preferences(user_id: str):
    preferences = db.preferences.find_one({"userId": user_id}, {"_id": 0})
    if not preferences:
        raise HTTPException(status_code=404, detail="Preferences not found")
    return preferences


@router.put("/api/preferences/{user_id}")
async def update_preferences(user_id: str, preferences: Preferences):
    result = db.preferences.update_one(
        {"userId": user_id},
        {"$set": preferences.dict()},
        upsert=True
    )
    return {"status": "updated" if result.matched_count else "created"}
