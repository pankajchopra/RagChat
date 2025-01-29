from fastapi import APIRouter, WebSocket
from starlette.websockets import WebSocketDisconnect

from app.database import db_connect, client
import asyncio

from app.semantic_search import SemanticSearch
from app.socket_connection_manager import SocketConnectionManager

router = APIRouter()
socket_connection_manager = SocketConnectionManager()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    db_connect()  # Initialize database connection
    try:
        while True:
            # WebSocketDisconnect is not raised unless we poll
            # https://github.com/tiangolo/fastapi/issues/3008
            try:
                data = await asyncio.wait_for(websocket.receive_text(), 0.2)
                # await socket_connection_manager.received_message(
                #     socket=websocket, message=data)
                semantic_search = SemanticSearch()
                llm_response = semantic_search.perform_rag_and_llm_search(data)

                await websocket.send_text(llm_response)
            except asyncio.TimeoutError:
                pass
    except WebSocketDisconnect:
        client.close()
        await websocket.close()
