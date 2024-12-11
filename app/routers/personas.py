from fastapi import APIRouter, HTTPException
from app.database import get_database
from app.models import Persona
from bson import ObjectId

router = APIRouter()
db = get_database()


@router.get("/api/personas")
async def get_personas():
    """
    Get all personas.

    This endpoint returns a list of all personas in the database,
    with their IDs, names, and backgrounds.

    **Parameters:**
        None

    **Responses:**
        A list of dictionaries, each containing the 'id', 'name', and 'background' of a persona.
        * `200`: List of personas
        * `500`: Internal server error
    """
    personas = list(db.personas.find({}, {"_id": 1, "name": 1, "background": 1}))
    for persona in personas:
        persona["id"] = str(persona["_id"])
        del persona["_id"]
    return personas


@router.post("/api/personas")
async def create_persona(persona: Persona):
    """
    Create a new persona.

    This endpoint creates a new persona document in the database
    based on the provided `Persona` object.

    **Parameters:**
        * `persona`: A `Persona` object, which should include the
          persona's `name` and `background`.

    **Responses:**
        A dictionary with a single key: `"id"`, which is the new persona's
        ID as a string.
    """

    persona_dict = persona.dict()
    result = db.personas.insert_one(persona_dict)
    return {"id": str(result.inserted_id)}


@router.delete("/api/personas/{persona_id}")
async def delete_persona(persona_id: str):
    """
    Delete a persona.

    This endpoint deletes a persona document in the database
    corresponding to the provided persona ID.

    **Parameters:**
        * `persona_id`: The ID of the persona to delete.

    **Responses:**
        A dictionary with a single key: `"status"`, which is `"deleted"`.
        * `200`: Persona deleted
        * `404`: Persona not found
    """
    result = db.personas.delete_one({"_id": ObjectId(persona_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Persona not found")
    return {"status": "deleted"}


@router.put("/personas/{persona_id}")
async def update_persona(persona_id: str, persona: Persona):
    """
    Update an existing persona.

    This endpoint updates the details of a persona document in the database
    using the provided `Persona` object, identified by `persona_id`.

    **Parameters:**
        * `persona_id`: The ID of the persona to update.
        * `persona`: A `Persona` object containing the updated persona details.

    **Responses:**
        A dictionary with a single key: `"status"`, which is `"updated"`.
        * `200`: Persona updated
        * `404`: Persona not found
    """

    result = db.personas.update_one(
        {"_id": ObjectId(persona_id)},
        {"$set": persona.dict(exclude={"id"})}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Persona not found")
    return {"status": "updated"}
