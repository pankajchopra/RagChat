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
                   tags=["preferences"],
                   responses={404: {"description": "Not found"}})
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
        user_id (str): The ID of the user whose preferences are to be retrieved.

    Returns:
        dict: A dictionary of the user's preferences if found.

    Raises:
        HTTPException: If no preferences are found for the given user ID, returns a 404 error.
    """

    preferences = db.get_collection("Preferences").find_one({"userId": user_id})
    if not preferences:
        raise HTTPException(status_code=404, detail="Preferences not found")
    return JSONResponse(document_to_dict(preferences))


@router.put("/preferences/{preference_id}")
async def update_preferences(preference_id: str, preference: Preferences):
    """
    Update a user's preferences.

    Args:
        preference_id (str): The ID of the user whose preferences are to be updated.
        preference (Preferences): The preferences to update to.

    Returns:
        A success message with either 'updated' or 'created' depending on
        whether the user already had preferences or not.
        """
    try:
        # Validate the ObjectId
        if not ObjectId.is_valid(preference_id):
            raise HTTPException(status_code=400, detail="Invalid ObjectId format")
        _id = ObjectId(preference_id)

        # Update the preference in MongoDB
        result = await db.get_collection("Preferences").update_one(
            {"_id": _id},
            {"$set": preference.dict()},
            upsert=True
        )

        if result.modified_count == 0:
            return {"status": "created"}
        else:
            return {"status": "updated"}
    except errors.InvalidId as e:  # Handle specific MongoDB ObjectId exceptions
        raise HTTPException(status_code=400, detail=f"Invalid ObjectId: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


@router.put("/preferences/{preference_id}")
async def update_preferences(preference_id: str, preference: Preferences):
    """
    Update a user's preferences.

    Args:
        preference_id (str): The ID of the user whose preferences are to be updated.
        preference (Preferences): The preferences to update to.

    Returns:
        A success message with either 'updated' or 'created' depending on
        whether the user already had preferences or not.
        """
    try:
        # Validate the ObjectId
        if not ObjectId.is_valid(preference_id):
            raise HTTPException(status_code=400, detail="Invalid ObjectId format")
        _id = ObjectId(preference_id)

        # Update the preference in MongoDB
        result = await db.get_collection("Preferences").update_one(
            {"_id": _id},
            {"$set": preference.dict()},
            upsert=True
        )

        if result.modified_count == 0:
            return {"status": "created"}
        else:
            return {"status": "updated"}
    except errors.InvalidId as e:  # Handle specific MongoDB ObjectId exceptions
        raise HTTPException(status_code=400, detail=f"Invalid ObjectId: {str(e)}")
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

        # Insert the preference into MongoDB
        result = await db.get_collection("Preferences").insert_one(
            {"_id": _id, **preference.dict()}
        )

        return {"preference_id": str(result.inserted_id)}

    except ValidationError as e:
        error_msg = []
        for err in e.errors():
            error_msg.append(f"{err['loc']}: {err['msg']}")
        raise HTTPException(status_code=422, detail="\n".join(error_msg))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

    @app.exception_handler(ValidationError)
    async def validation_exception_handler(request, exc):
        logger.error("Validation error: %s", exc)
        return HTTPException(status_code=422, detail=str(exc))