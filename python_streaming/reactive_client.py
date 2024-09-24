"""Consume an HTTP stream with a reactive programming approach."""

import reactivex as rx
from reactivex import operators as ops
from urllib3 import PoolManager


http = PoolManager()
BUFFER_SIZE = 80


def buffer_response_reactively(user_prompt: str):
    """Perform an HTTP request with a chunked (streamed) response and consume
    it reactively, with further processing."""
    request_payload = {
        'user_id': '12345',
        'message': user_prompt,
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
            ops.buffer_with_count(BUFFER_SIZE),
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
    prompt = "Tell me a joke about pirates in the tone of Barack Obama"
    buffer_response_reactively(prompt)
