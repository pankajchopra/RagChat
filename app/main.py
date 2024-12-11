from fastapi import FastAPI, APIRouter
from fastapi.openapi.utils import get_openapi
from app.routers import personas,preferences,conversations
from app import websocket
from fastapi_socketio import SocketManager
# from app.auth import oauth2_scheme
from app.database import load_env
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

api_router = APIRouter()
# load environment variables
load_env()
app = FastAPI()

# CORS middleware for frontend-backend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000"],  # Frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
# api_router.include_router(conversations_router, tags=["conversations"])
# api_router.include_router(personas_router, tags=["personas"])
# api_router.include_router(preferences_router)
# api_router.include_router(endpoint_router)
app.include_router(conversations.router, tags=["conversations"])
app.include_router(personas.router, tags=["personas"])
app.include_router(preferences.router)
app.include_router(websocket.router)
# Include routers for modularity
# app.include_router(oauth2_scheme)

api_router.include_router(conversations.router)
api_router.include_router(personas.router)
api_router.include_router(preferences.router)
app.include_router(websocket.router)

openapi_schema = get_openapi(
    title="My FastAPI App",
    description="This is my FastAPI app",
    version="1.0.0",
    openapi_version="3.0.2",
    contact={
        "name": "Pankaj Kumar",
        "email": "pkchop@gmail.com",
        "url": "https://www.yourwebsite.com",
    },
    routes=api_router.routes
)

app.openapi_schema = openapi_schema
# WebSocket manager
socket_manager = SocketManager(app)


# def startup():
#     db_connect()  # Initialize database connection
#     print("App started")


# @asynccontextmanager
# async def lifespan(FastAPI):
#     # Startup logic
#     db_connect()  # Initialize database connection
#     print("App started")
#
#     yield
#
#     # Shutdown logic
#     client.close()
#     print("App shutdown")


# async def shutdown_event():
#     # Your shutdown code here
#     print("App shut down")


if __name__ == "__main__":

    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="debug", log_config=None)
