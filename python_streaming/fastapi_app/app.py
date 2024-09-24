"""FastAPI application with example endpoints for streaming."""

import asyncio
from pathlib import Path
from pprint import pprint
from typing import Annotated

from fastapi import FastAPI, Header, Query, Response
from fastapi.websockets import WebSocket
from fastapi.responses import StreamingResponse, FileResponse
import soundfile as sf

from python_streaming import chatting_service
from python_streaming.audio import read_audio_frames, BUFFER_SIZE, frames_to_bytes, RANGED_REQUEST_BUFFERS, \
    extract_bit_depth
from python_streaming.fastapi_app.dto import ChatRequestDto
from python_streaming.util import iterate_over_audio, iterate_over_json_data


app = FastAPI(title="HTTP streaming example")


@app.get("/audios/file-stream")
def get_audio_file_stream(
    audio_format: Annotated[str | None, Query(examples=["mp3", "wav"])] = "mp3"
):
    # Stream a chunked response directly from a pre-loaded file.
    # You only need a path to the file and the media type.
    # This option is faster than streaming from an iterator.
    return FileResponse(
        f"resources/audio.{audio_format}",
        media_type="audio/mpeg"
    )


@app.get("/audios/streaming-response")
def get_audio_streaming_response():
    # Stream a chunked response from an iterator.
    # This option is slower than streaming from a pre-loaded file (FileResponse),
    # but it allows you to serve the data on the fly, while some other service
    # is producing it upstream.
    return StreamingResponse(
        iterate_over_audio(),
        media_type="audio/mpeg",
    )


@app.get("/data/stream")
def get_data_http_stream():
    # Stream a chunked response from an iterator.
    # This option is slower than streaming from a pre-loaded file (FileResponse),
    # but it allows you to serve the data on the fly, while some other service
    # is producing it upstream.
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


@app.get("/videos/buffering")
async def video_buffering(range: str = Header(None)):  # TODO: clarify header
    video_path = "resources/video.mp4"
    start, end = range.replace("bytes=", "").split("-")
    start = int(start)
    end = int(end) if end else start + 1024 * 1024  # Default chunk size

    with open(video_path, "rb") as video:
        video.seek(start)
        data = video.read(end - start)
        return StreamingResponse(
            content=data,
            media_type="video/mp4",
            headers={
                "Content-Range": f"bytes {start}-{end}/{video.stat().st_size}",
                "Accept-Ranges": "bytes"
            }
        )


@app.get("/audios/{audio_id}")
async def get_audio_info(audio_id: str):
    if audio_id != "1":
        return Response({"error": "Audio not found"}, status_code=404)
    audio_path = Path("resources/audio.wav")
    audio_info = sf.info(str(audio_path))
    return {
        "audio_id": audio_id,
        "format": audio_info.format,
        "sample_rate": audio_info.samplerate,
        "bit_depth": extract_bit_depth(audio_info.extra_info),
        "channels": audio_info.channels,
        "content_length": "*",
    }

@app.get("/audios/frame-buffers/{audio_id}")
async def audio_frame_buffering(audio_id: str, start_frame: Annotated[int, Query(ge=0)] = 0):
    if audio_id != "1":
        return Response({"error": "Audio not found"}, status_code=404)
    audio_path = Path("resources/audio.wav")
    audio_info = sf.info(str(audio_path))
    number_of_frames = BUFFER_SIZE * RANGED_REQUEST_BUFFERS
    pprint(f"Requested frames: {start_frame}-{start_frame + number_of_frames}")
    start_byte_position = frames_to_bytes(start_frame, extract_bit_depth(audio_info.extra_info), audio_info.channels)
    response_byte_length = frames_to_bytes(number_of_frames, extract_bit_depth(audio_info.extra_info), audio_info.channels)

    data = read_audio_frames(audio_path, start_frame, number_of_frames)
    return Response(
        content=data,
        media_type="application/octet-stream",
        headers={
            "Content-Range": f"bytes {start_byte_position}-{start_byte_position+response_byte_length}/*",
            "Frame-Range": f"frames {start_frame}-{start_frame + number_of_frames}/*",
            "Accept-Ranges": "frames",
        }
    )


# @app.get("/audios/byte-buffers")
# async def audio_buffering(range: str = Header(None)):
#     # TODO: implement with wave file
#     audio_path = "resources/audio.mp3"
#     start, end = range.replace("bytes=", "").split("-")
#     start = int(start)
#     end = int(end) if end else start + 16 * 1024  # Default chunk size: 16 KB
#
#     read_audio_frames(audio_path, start, end)
#     return StreamingResponse(
#         data,
#         media_type="audio/mpeg",
#         headers={
#             "Content-Range": f"bytes {start}-{end}/{audio.stat().st_size}",
#             "Accept-Ranges": "bytes"
#         }
#     )


@app.post("/chat")
async def get_ai_response(chat_request: ChatRequestDto):
    # The chatting service exposes a generator that iterates over Bedrock response events
    bedrock_streaming_response = await chatting_service.chat(chat_request.message)

    # Stream the response directly from the generator
    return StreamingResponse(
        bedrock_streaming_response,
        media_type="text/plain"
    )


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="localhost", port=5000)
