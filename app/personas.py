from fastapi import APIRouter, HTTPException
from app.database import get_database
from app.models import Persona
from bson import ObjectId

router = APIRouter()
db = get_database()

@router.get("/personas")
def get_personas():
    personas = list(db.personas.find({}, {"_id": 1, "name": 1, "background": 1}))
    for persona in personas:
        persona["id"] = str(persona["_id"])
        del persona["_id"]
    return personas

@router.post("/personas")
def create_persona(persona: Persona):
    persona_dict = persona.dict()
    result = db.personas.insert_one(persona_dict)
    return {"id": str(result.inserted_id)}

@router.delete("/personas/{persona_id}")
def delete_persona(persona_id: str):
    result = db.personas.delete_one({"_id": ObjectId(persona_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Persona not found")
    return {"status": "deleted"}

@router.put("/personas/{persona_id}")
def update_persona(persona_id: str, persona: Persona):
    result = db.personas.update_one(
        {"_id": ObjectId(persona_id)},
        {"$set": persona.dict(exclude={"id"})}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Persona not found")
    return {"status": "updated"}
