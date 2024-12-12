from bson import ObjectId, errors
from fastapi import APIRouter, HTTPException   
from fastapi.responses import JSONResponse
from app.database import get_database
from app.models import Persona
from app.RAG.utils import document_to_dict
import logging

logger = logging.getLogger(__name__)

router = APIRouter()
db = get_database()

router = APIRouter(prefix="/api", tags=["personas"])

@router.get("/personas/all")
async def get_all_personas():
    """
    Retrieve all personas.

    Returns a list of all personas in the database.

    Args:
        None

    Returns:
        list[dict]: A list of dictionaries containing the personas.
    """
    try:
        _persona = []
        personas = get_database().Personas.find({})
        for persona in personas:
            _persona.append(document_to_dict(persona))
        return JSONResponse(_persona)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/personas/{persona_id}")
async def get_persona(persona_id: str):
    """
    Retrieve a persona by its ID.

    Args:
        persona_id (str): The ID of the persona to retrieve.

    Returns:
        The retrieved persona as a dictionary.

    Raises:
        HTTPException: If the persona could not be found.
    """
    persona = get_database().Personas.find_one({"_id": ObjectId(persona_id)})
    if not persona:
        raise HTTPException(status_code=404, detail="Persona not found")
    return JSONResponse(document_to_dict(persona))


@router.post("/personas")
async def create_persona(persona: Persona):
    """
    Create a new persona.

    This endpoint creates a new persona document in the database,
    based on the provided `Persona` object.

    **Parameters:**
        * `persona`: A `Persona` object, which should include any desired fields.

    **Responses:**
        A dictionary with a single key: `"id"`, which is the ID of the newly created persona.

    **Raises:**
        HTTPException: If the persona could not be created.
    """
    logger.info("Received request: %s", persona)

    # Create a new ObjectId for the preference
    _id = ObjectId()
    print(persona.dict())
    # Insert the preference into MongoDB
    result = db.get_collection("Preferences").insert_one(
        {"_id": _id, **persona.dict()}
    )
    return {"id": str(result.inserted_id)}



@router.put("/personas")
async def update_persona(persona: Persona):
    """
    Update a persona.

    Args:
        persona (Persona): The updated persona.

    Returns:
        A success message with either 'updated' or 'created' depending on
        whether the persona already existed or not.
    """
    try:
        logger.info("Received request: %s", persona)
        if persona.dict().get("id") is None:
            raise HTTPException(status_code=400, detail="Bad Request: Missing id field in request body. Invalid ObjectId format")
        # Validate the ObjectId
        if not ObjectId.is_valid(persona.dict().get("id")):
            raise HTTPException(status_code=400, detail="Invalid ObjectId format")
        _id = ObjectId(persona.dict().get("id"))

        # Update the persona in MongoDB
        result = get_database().Personas.update_one(
            {"_id": _id},
            {"$set": persona.dict()},
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


@router.delete("/personas/{persona_id}")
async def delete_persona(persona_id: str):
    """
    Delete a persona from the database.
    
    This endpoint deletes a persona document from the database, identified by
    the provided `persona_id`.
    
    **Parameters:**
        * `persona_id`: The ID of the persona to delete.
    
    **Responses:**
        * A dictionary with a single key: `"status"`, which is `"deleted"`.
        
    **Raises:**
        HTTPException: If the persona could not be found.
    """
    try:
        result = get_database().Personas.delete_one({"_id": ObjectId(persona_id)})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Persona not found")
        return {"status": "deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
