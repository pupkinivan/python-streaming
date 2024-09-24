"""Consume a ranged or streamed audio file from a remote server."""
import asyncio
import json
from pathlib import Path
from pprint import pprint
from queue import SimpleQueue, Queue
import time
from typing import Optional

from python_streaming.audio import play_sound_from_iterator, frames_to_bytes

import urllib3

from config import HTTP_PORT, RANGED_REQUEST_BUFFERS, BUFFER_SIZE


http = urllib3.PoolManager()


async def buffer_remote_file(
    audio_id: str,
    number_of_frames: int,
    fifo_queue: SimpleQueue,
):
    """Buffer a remote file by requesting chunks of data from the server.

    Args:
        audio_id (str): The audio file's ID.
        number_of_frames (int): The number of frames to request from the
            server. A frame is an instant's sample, for all given channels.
        fifo_queue (deque): The FIFO queue to store the audio data.

    Returns:
        None
    """
    current_frame = 0
    do_read_more = True
    while do_read_more:
        if fifo_queue.qsize() == 10:
            await asyncio.sleep(0.01)
            continue
        response = http.request(
            'GET',
            f'http://localhost:{HTTP_PORT}/audios/frame-buffers/{audio_id}',
            fields={"start_frame": current_frame}
        )
        # pprint(response.headers)
        last_received_frame = int(response.headers.get("Frame-Range").split('-')[1].split('/')[0])
        frames_read = last_received_frame - current_frame if current_frame > 0 else last_received_frame
        if frames_read < number_of_frames:
            do_read_more = False
        current_frame = last_received_frame
        fifo_queue.put_nowait(response.data)


async def wait_for_queue(queue: SimpleQueue, retry_times: int = 5):
    empty_counter = 0
    while (queue_size := queue.qsize()) == 0:
        print("Waiting for buffer...")
        empty_counter += 1
        if empty_counter == retry_times:
            print("Queue has been empty for some time. Exiting...")
            exit(0)
        await asyncio.sleep(0.1)
    pprint(f"Queue size: {queue_size}")
    pprint("Reading from buffer queue")
    next_buffer = queue.get_nowait()
    return next_buffer


async def buffer_and_read(audio_id: str, number_of_frames: int):
    buffers_queue = SimpleQueue()
    buffering_task = asyncio.create_task(
        buffer_remote_file(audio_id, number_of_frames, buffers_queue)
    )
    while True:
        next_buffer = await wait_for_queue(buffers_queue)
        yield next_buffer


def consume_wave_file_by_bytes(audio_file_id: str):
    # Request audio from server and iterate until all content has been received

    # 1st, request the audio file's metadata
    response = http.request('GET', f'http://localhost:{HTTP_PORT}/audios/{audio_file_id}')
    if response.status != 200:
        print(f"Error: {response.status} - {response.data.decode('utf-8')}")
        raise ValueError("Error retrieving audio metadata")
    response = response.json()

    # We're assuming the format is WAV
    channels = response.get("channels")
    sample_rate = response.get("sample_rate")
    bit_depth = response.get("bit_depth")
    content_length = response.get("content_length", None)
    if content_length in ('*', None):
        content_length = None
    # We want to request samples x channels [bytes]
    ranged_request_size = RANGED_REQUEST_BUFFERS * BUFFER_SIZE * channels


    # play_sound_from_iterator(
    #     audio_data_iterator=buffer_remote_file(ranged_request_size, content_length),
    #     output_file_path=Path(f"resources/audio_{audio_file_id}.wav"),
    #     bit_depth=bit_depth,
    #     number_of_channels=channels,
    #     sample_rate=sample_rate,
    #     buffer_size=ranged_request_size,
    # )


async def consume_wave_file_by_frames(audio_file_id: str):
    # Request audio from server and iterate until all content has been received

    # 1st, request the audio file's metadata
    response = http.request('GET', f'http://localhost:{HTTP_PORT}/audios/{audio_file_id}')
    if response.status != 200:
        print(f"Error: {response.status} - {response.data.decode('utf-8')}")
        raise ValueError("Error retrieving audio metadata")
    response = response.json()

    # We're assuming the format is WAV
    channels = response.get("channels")
    sample_rate = response.get("sample_rate")
    bit_depth = response.get("bit_depth")
    content_length = response.get("content_length", None)

    number_of_frames = BUFFER_SIZE * RANGED_REQUEST_BUFFERS

    await play_sound_from_iterator(
        audio_data_iterator=buffer_and_read(),
        output_file_path=Path(f"resources/audio_{audio_file_id}.wav"),
        bit_depth=bit_depth,
        number_of_channels=channels,
        sample_rate=sample_rate,
        buffer_size=number_of_frames,
    )


if __name__ == '__main__':
    asyncio.run(consume_wave_file_by_frames(audio_file_id="1"))
