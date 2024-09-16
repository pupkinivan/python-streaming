"""FastAPI application with example endpoints for streaming."""

import asyncio

from fastapi import FastAPI
from fastapi.websockets import WebSocket
from fastapi.responses import StreamingResponse, FileResponse

from python_streaming.util import iterate_over_audio, iterate_over_json_data


app = FastAPI(title="HTTP streaming example")


@app.get("/audios/file-stream")
def get_audio_file_stream():
    return FileResponse(
        "resources/audio.mp3",
        media_type="audio/mpeg"
    )


@app.get("/audios/streaming-response")
def get_audio_streaming_response():
    return StreamingResponse(
        iterate_over_audio(),
        media_type="audio/mpeg"
    )


@app.get("/data/stream")
def get_data_http_stream():
    return StreamingResponse(
        iterate_over_json_data(),
        media_type="application/json"
    )


@app.websocket("/data/websocket")
async def websocket_endpoint(websocket: WebSocket):
    data_iterator = iterate_over_json_data()
    await websocket.accept()
    try:
        while new_data := next(data_iterator):
            await asyncio.sleep(0.1)
            await websocket.send_text(new_data)
    except StopIteration:
        pass
    finally:
        await websocket.close()


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)
