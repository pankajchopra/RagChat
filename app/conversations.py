from fastapi import APIRouter, HTTPException
from app.database import get_database
from app.models import Conversation
from bson import ObjectId

router = APIRouter()
db = get_database()


@router.get("/api/conversations")
async def get_conversations():
    conversations = list(db.conversations.find({}, {"_id": 1, "name": 1}))
    for conv in conversations:
        conv["id"] = str(conv["_id"])
        del conv["_id"]
    return conversations


@router.post("/api/conversations")
async def create_conversation(conversation: Conversation):
    conversation_dict = conversation.dict()
    result = db.conversations.insert_one(conversation_dict)
    return {"id": str(result.inserted_id)}


@router.delete("/api/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str):
    result = db.conversations.delete_one({"_id": ObjectId(conversation_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"status": "deleted"}


@router.put("/api/conversations/{conversation_id}")
async def update_conversation(conversation_id: str, conversation: Conversation):
    result = db.conversations.update_one(
        {"_id": ObjectId(conversation_id)},
        {"$set": conversation.dict(exclude={"id"})}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"status": "updated"}
