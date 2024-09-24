"""An example of how to consume a text/plain response that's being streamed, from the HTTP client side."""
from typing import Iterator

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


if __name__ == '__main__':
    user_prompt = 'Tell me a short story about pirates in the tone of a physicist'
    try:
        response_iterator = consume_chat_response(user_prompt, do_print=True)
        while True:
            next(response_iterator)
    except StopIteration:
        print('\n\nDone!\n\n')
