from fastapi import FastAPI, APIRouter
from contextlib import asynccontextmanager
from app.conversations import router as conversations_router
from app.personas import router as personas_router
from app.preferences import router as preferences_router
from app.websocket import router as endpoint_router
from fastapi_socketio import SocketManager
# from app.auth import oauth2_scheme
from app.database import db_connect, client, load_env
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

api_router = APIRouter()
# load environment variables
load_env()
app = FastAPI(    title="My FastAPI App",
    description="This is my FastAPI app",
    version="1.0.0",
    openapi_url="/openapi.json",
    openapi_tags=[
        {"name": "Conversations", "description": "Conversations-related endpoints"},
        {"name": "Personas", "description": "personas-related endpoints"},
        {"name": "Preferences", "description": "Preferences-related endpoints"}
    ],
    openapi_prefix="/api",
    openapi_info={
        "contact": {"name": "Pankaj Kumar", "email": "pkchopra@gmail.com"},
        "license": {"name": "MIT"}
    }
                  )

# CORS middleware for frontend-backend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000"],  # Frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
api_router.include_router(conversations_router,prefix="/conversations", tags=["conversations"])
api_router.include_router(personas_router, prefix="/personas", tags=["personas"])
api_router.include_router(preferences_router, prefix="/preferences", tags=["preferences"])
api_router.include_router(endpoint_router)
# Include routers for modularity
# app.include_router(oauth2_scheme)

# WebSocket manager
socket_manager = SocketManager(app)


# def startup():
#     db_connect()  # Initialize database connection
#     print("App started")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    db_connect()  # Initialize database connection
    print("App started")

    yield

    # Shutdown logic
    client.close()
    print("App shutdown")


# async def shutdown_event():
#     # Your shutdown code here
#     print("App shut down")


if __name__ == "__main__":

    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="debug",log_config=None)
