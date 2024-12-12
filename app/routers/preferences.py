from bson import ObjectId, errors
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from app.database import get_database
from app.models import Preferences
from app.RAG.utils import document_to_dict
from pydantic import ValidationError
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api",
                   tags=["preferences"])
db = get_database()


@router.get("/preferences/all", response_model=list[Preferences])
async def get_all_preferences():
    """
    Retrieve all user's preferences.

    Returns:
        dict: A list of dictionaries of all the users preferences .

    Raises:
        HTTPException: If no preferences are found for the given user ID, returns a 404 error.
    """
    try:
        _preferences = []
        preferences = db.get_collection("Preferences").find({})
        if not preferences:
            raise HTTPException(status_code=404, detail="Preferences not found")
        else:
            for preference in preferences:
                _preferences.append(document_to_dict(preference))
        return JSONResponse(_preferences)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/preferences/{user_id}")
async def get_preferences(user_id: str):
    """
    Retrieve a user's preferences.

    Args:
        user_id (str): The user_id of the user whose preferences are to be retrieved.

    Returns:
        dict: A dictionary of the user's preferences if found.

    Raises:
        HTTPException: If no preferences are found for the given user ID, returns a 404 error.
    """

    preferences = db.get_collection("Preferences").find_one({"userId": user_id})
    if not preferences:
        raise HTTPException(status_code=404, detail="Preferences not found")
    return JSONResponse(document_to_dict(preferences))


@router.get("/preferences/{id}")
async def get_preferences_by_id(id: str):
    """
    Retrieve a user's preferences.

    Args:
        id (str): The ID of the user whose preferences are to be retrieved.

    Returns:
        dict: A dictionary of the user's preferences if found.

    Raises:
        HTTPException: If no preferences are found for the given user ID, returns a 404 error.
    """

    try:
        preferences = db.get_collection("Preferences").find_one({"_id": ObjectId(id)})
        if not preferences:
            raise HTTPException(status_code=404, detail="Preferences not found")
        return JSONResponse(document_to_dict(preferences))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/preferences")
async def update_preferences(preference: Preferences):
    """
    Update a user's preferences.

    Args:
        preference (Preferences): The preferences to update to.

    Returns:
        A success message with either 'updated' or 'created' depending on
        whether the user already had preferences or not.
        """
    try:
        if preference.dict().get("id") is None:
            raise HTTPException(status_code=400, detail="Bad Request: Missing id field in request body. Invalid ObjectId format")
        # Validate the ObjectId
        if not ObjectId.is_valid(preference.dict().get("id")):
            raise HTTPException(status_code=400, detail="Invalid ObjectId format")
        _id = ObjectId(preference.dict().get("id"))

        # Update the preference in MongoDB
        result = db.get_collection("Preferences").update_one(
            {"_id": _id},
            {"$set": preference.dict()},
            upsert=False
        )

        if result.modified_count == 1:
            return {"status": "updated", "modified": result.modified_count}
    except errors.InvalidId as e:  # Handle specific MongoDB ObjectId exceptions
        raise HTTPException(status_code=400, detail=f" Bad Request:Invalid ObjectId: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


@router.post("/preferences")
async def create_preference(preference: Preferences):
    """
    Creates a new user preference.

    Args:
        preference (Preferences): The new preference to be created.

    Returns:
        The ID of the newly created preference.
    """

    try:
        logger.info("Received request: %s", preference)

        # Create a new ObjectId for the preference
        _id = ObjectId()
        print(preference.dict())
        # Insert the preference into MongoDB
        result = db.get_collection("Preferences").insert_one(
            {"_id": _id, **preference.dict()}
        )

        return {"id": str(result.inserted_id)}

    except ValidationError as e:
        error_msg = []
        for err in e.errors():
            error_msg.append(f"{err['loc']}: {err['msg']}")
        raise HTTPException(status_code=422, detail="\n".join(error_msg))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


@router.delete("/preferences/{id}")
async def delete_Preference(preference_id: str):
    """
    Delete a Preference from the database.

    This endpoint deletes a Preferences document from the database, identified by
    the provided `preference_id`.

    **Parameters:**
        * `preference_id`: The ID of the Preference to delete.

    **Responses:**
        * A dictionary with a single key: `"status"`, which is `"deleted"`.

    **Raises:**
        HTTPException: If the Preference could not be found.
    """
    try:
        result = get_database().Preferences.delete_one({"_id": ObjectId(preference_id)})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail=f"Preference({preference_id}) not found in the database")
        return {"status": "deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
