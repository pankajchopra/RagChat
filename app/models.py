from pydantic import BaseModel
from typing import Optional, List
import uuid


# Conversation Model
class Conversation(BaseModel):
    id: Optional[str]
    query: str
    context: str
    response: str

    def __init__(self, query, context, response):
        self.id = str(uuid.uuid4())
        self.query = query
        self.context = context
        self.response = response

    def get_query(self):
        return self.query

    def get_context(self):
        return self.Context

    def get_response(self):
        return self.response

    def get_query_with_context(self):
        return {"query": self.query, "Context": self.Context}

    def get_all(self):
        return {"id": self.id, "query": self.query, "Context": self.Context, "response": self.response}


class GeminiResponse:
    def __init__(self, message, intent, entities, metadata):
        self.message = message
        self.intent = intent
        self.entities = entities
        self.metadata = metadata


# Persona Model
class Persona(BaseModel):
    id: Optional[str]
    name: str
    background: str


# Preferences Model
class Preferences(BaseModel):
    id: Optional[str]
    userId: str
    name: str
    fontSize: Optional[str] = "medium"
    fontFamily: Optional[str] = "sans-serif"
    chatHistoryLength: Optional[str] = 100
    autoScroll: Optional[bool] = True
    showTimestamps: Optional[bool] = True
    imageUploadEnabled: Optional[bool] = True
    archiveEnabled: Optional[bool] = True
    theme: Optional[str] = "dark"
    avatar: Optional[str] = "default"
    language: Optional[str] = "en"
    notificationSound: Optional[bool] = True
    showAvatars: Optional[bool] = True
    customKeywords: Optional[List] = ["keyword1", "keyword2"],
    preferredLLMs: Optional[List] = ["openai", "gemini", "LAMA"]
