"""An example of how to consume a text/plain response that's being streamed, from the HTTP client side."""
from typing import Iterator

import urllib3


http = urllib3.PoolManager()


def print_streamed_chat_response(prompt: str):
    request_payload = {
        'user_id': '12345',
        'message': prompt,
    }
    # If you're not using the with context manager, you MUST close the response object!!!
    # That releases the connection back to the pool.
    with http.request(
        'POST',
        'http://localhost:5000/chat',
        json=request_payload,
        preload_content=False,
    ) as response:
        for chunk in response.stream():
            print(chunk.decode('utf-8'), end='')


def consume_chat_response(prompt: str) -> Iterator[str]:
    request_payload = {
        'user_id': '12345',
        'message': prompt,
    }
    # If you're not using the with context manager, you MUST close the response object!!!
    # That releases the connection back to the pool.
    with http.request(
        'POST',
        'http://localhost:5000/chat',
        json=request_payload,
        preload_content=False,
    ) as response:
        for chunk in response.stream():
            yield chunk.decode('utf-8')


if __name__ == '__main__':
    user_prompt = 'Tell me a short story about pirates in the tone of a phyisicist'
    print_streamed_chat_response(user_prompt)
