from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.conversations import router as conversations_router
from app.personas import router as personas_router
from app.preferences import router as preferences_router
from fastapi_socketio import SocketManager
# from app.auth import oauth2_scheme
from app.database import db_connect, client
from fastapi.middleware.cors import CORSMiddleware

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
app.include_router(conversations_router, prefix="/conversations", tags=["conversations"])
app.include_router(personas_router, prefix="/personas", tags=["personas"])
app.include_router(preferences_router, prefix="/preferences", tags=["preferences"])

# Include routers for modularity
# app.include_router(oauth2_scheme)

# WebSocket manager
socket_manager = SocketManager(app)


def startup():
    db_connect()  # Initialize database connection
    print("App started")


# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     # Startup logic
#     db_connect()  # Initialize database connection
#     print("App started")
#
#     yield
#
#     # Shutdown logic
#     client.close()
#     print("App shutdown")


async def shutdown_event():
    # Your shutdown code here
    print("App shut down")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)