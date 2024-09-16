# Streaming in Python

Here are a few examples on how to stream web responses in Python, both using WebSockets and HTTP.

The project's build system is Poetry and I'm using Python 3.11 or 3.12. Clone the repo and run `poetry install`.

## WebSockets

Run `python python_streaming/websockets/server.py` and `python python_streaming/websockets/client.py` in two different terminals.

## HTTP

This part of the project uses FastAPI to handle both HTTP and other WebSocket endpoints.

Run `python python_streaming/http/app.py` and then invoke each of the different endpoints using your HTTP/WebSockets client of choice. The endpoints aren't fully documented, but I'm persisting the OpenAPI docs in the `openapi_docs.json` file, because I'm extremely creative at file naming.
