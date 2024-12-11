from fastapi import APIRouter, HTTPException
from app.database import get_database
from app.models import Conversation
from bson import ObjectId

router = APIRouter()
db = get_database()


@router.get("/conversations/")
async def get_conversations():
    """
    Get a list of all conversations.

    Returns a list of dictionaries, each containing an `id` and a `name`.
    """
    conversations = list(db.conversations.find({}, {"_id": 1, "name": 1}))
    for conv in conversations:
        conv["id"] = str(conv["_id"])
        del conv["_id"]
    return conversations


@router.post("/conversations")
async def create_conversation(conversation: Conversation):
    """
    Create a new conversation.

    This endpoint creates a new conversation document in the database,
    based on the provided `Conversation` object.

     **Parameters:**
        * `conversation`: A `Conversation` object, which should include the
            conversation's `name` and any other desired fields.

     **Responses:**
        A dictionary with a single key: `"id"`, which is the new conversation's
        ID as a string.
     * `200`: A list of user objects
     * `500`: Internal server error
    Raises:
        HTTPException: If the conversation could not be created.
    """
    conversation_dict = conversation.dict()
    result = db.conversations.insert_one(conversation_dict)
    return {"id": str(result.inserted_id)}


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """
    Delete an existing conversation.

    This endpoint deletes a conversation document from the database,
    identified by the provided conversation ID.

    **Parameters:**
        * `conversation_id`: The ID of the conversation to delete.

    **Responses:**
        A dictionary with a single key: `"status"`, which is `"deleted"`.

    **Raises:**
        HTTPException: If the conversation could not be found.
    """

    result = db.conversations.delete_one({"_id": ObjectId(conversation_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"status": "deleted"}


@router.put("/conversations/{conversation_id}")
async def update_conversation(conversation_id: str, conversation: Conversation):
    """
    Update an existing conversation.

    This endpoint updates a conversation document in the database,
    based on the provided `Conversation` object.

    **Parameters:**
        * `conversation_id`: The ID of the conversation to update.
        * `conversation`: A `Conversation` object, which should include any
            fields to update.

    **Responses:**
        A dictionary with a single key: `"status"`, which is `"updated"`.

    **Raises:**
        HTTPException: If the conversation could not be updated.
    """
    result = db.conversations.update_one(
        {"_id": ObjectId(conversation_id)},
        {"$set": conversation.dict(exclude={"id"})}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"status": "updated"}
