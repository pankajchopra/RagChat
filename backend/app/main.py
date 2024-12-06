from fastapi import FastAPI, WebSocket
from app.conversations import router as conversations_router
from app.personas import router as personas_router
from app.preferences import router as preferences_router
from fastapi_socketio import SocketManager
from app.websocket import websocket_endpoint
from app.auth import oauth2_scheme
from app.database import db_connect
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS middleware for frontend-backend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(conversations_router, prefix="/conversations", tags=["conversations"])
app.include_router(personas_router, prefix="/personas", tags=["personas"])
app.include_router(preferences_router, prefix="/preferences", tags=["preferences"])

# WebSocket manager
socket_manager = SocketManager(app)

# Include routers for modularity
app.include_router(websocket_endpoint)
app.include_router(oauth2_scheme)

@app.on_event("startup")
def startup():
    db_connect()  # Initialize database connection
