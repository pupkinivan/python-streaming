# Streaming recipes for Python

Here are a few examples on how to stream web responses in Python, both using WebSockets and HTTP.

The project's build system is Poetry and I'm using Python 3.11 or 3.12. Clone the repo and run `poetry install`.

## WebSockets

Run `python python_streaming/websockets/server.py` and `python python_streaming/websockets/client.py` in two different terminals.

## HTTP

There are examples for streaming responses in two widely used frameworks: FastAPI and Flask. This part of the project uses FastAPI to handle both HTTP and other WebSocket endpoints.

1. Set the environment variables in the `.env` file (you have an `.env.sample` available for reference) 
2. Run the FastAPI or Flask apps (`python_streaming/fastapi_app/app.py` or `python_streaming/flask_app/app.py`, respectively)
3. Invoke each of the different endpoints using your HTTP/WebSockets client of choice (remember _not_ to preload the response). You have a few examples:
   - `python_streaming/chat_client.py` leverages the streamed response
   - `python_streaming/reactive_client.py` provides a demonstration of how to further connect the incoming stream with reactive programming observables

The endpoints for the FastAPI aren't fully documented, but I'm persisting the OpenAPI docs in the `openapi_docs.json` file.
