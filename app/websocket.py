from fastapi import APIRouter, WebSocket
from google.cloud import speech
from starlette.websockets import WebSocketDisconnect

from app.RAG.query import run_query_with_rag_and_then_with_gemini
from app.database import db_connect, client
import asyncio

from app.socket_connection_manager import SocketConnectionManager
router = APIRouter()

speech_client = speech.SpeechClient()
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
                if data.startswith("audio-query:"):
                    audio_base64 = data[len("audio-query:"):]
                    transcript = transcribe_audio(audio_base64)
                    llm_response = run_query_with_rag_and_then_with_gemini(transcript)
                else:
                    llm_response = run_query_with_rag_and_then_with_gemini(data)

                await websocket.send_text(llm_response)
            except asyncio.TimeoutError:
                pass
    except WebSocketDisconnect:
        client.close()
        await websocket.close()


def transcribe_audio(audio_base64: str) -> str:
    audio = speech.RecognitionAudio(content=audio_base64)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code="en-US",
    )
    response = speech_client.recognize(config=config, audio=audio)
    transcript = " ".join([result.alternatives[0].transcript for result in response.results])
    return transcript
