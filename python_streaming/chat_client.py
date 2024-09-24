"""An example of how to consume a text/plain response that's being streamed, from the HTTP client side."""

from typing import Iterator

import reactivex as rx
from reactivex import operators as ops
import urllib3


http = urllib3.PoolManager()


def consume_chat_response(prompt: str, do_print: bool = False) -> Iterator[str]:
    """Invoke the streamed chat endpoint and yield as each chunk is received."""
    request_payload = {
        'user_id': '12345',
        'message': prompt,
    }
    # If you're not using the with context manager, you MUST close the response object!!!
    # That releases the connection back to the pool.
    # Other streaming and async compatible libraries include httpx and aiohttp,
    # do take a look at them!
    with http.request(
        'POST',
        'http://localhost:5000/chat',
        json=request_payload,
        preload_content=False,
    ) as response:
        for chunk in response.stream():
            text_chunk = chunk.decode('utf-8')
            if do_print:
                print(text_chunk, end='')
            yield chunk


def buffer_response_reactively(prompt: str):
    """Perform an HTTP request with a chunked (streamed) response and consume
    it reactively, with further processing."""
    request_payload = {
        'user_id': '12345',
        'message': prompt,
    }
    # If not using the with context manager, you MUST .close() the response object!!!
    response = http.request(
        'POST',
        'http://localhost:5000/chat',
        json=request_payload,
        preload_content=False
    )

    # Here's the reactive part of the code, with mapping, flat-mapping,
    # buffering, etc.
    (
        rx.from_iterable(response.stream())
        .pipe(
            ops.map(lambda bytes_chunk: bytes_chunk.decode('utf-8')),
            ops.flat_map(lambda text: [character for character in text]),
            ops.buffer_with_count(80),  # Pick a buffer size or time window
            ops.map(lambda characters: ''.join(characters)),
        )
        .subscribe(
            on_next=lambda text: print(text, end='\n\n'),
            on_error=lambda e: print(f'Error: {e}'),
            on_completed=lambda: print('Done'),
        )
    )
    response.close()


if __name__ == '__main__':
    user_prompt = 'Tell me a short story about pirates in the tone of a physicist'

    # Run either the reactive consumer:
    # buffer_response_reactively(user_prompt)
    # Or the imperative one:
    try:
        response_iterator = consume_chat_response(user_prompt, do_print=True)
        while True:
            next(response_iterator)
    except StopIteration:
        print('\n\nDone!\n\n')
