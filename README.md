# Streaming recipes for Python

Here are a few examples on how to stream web responses in Python, both using WebSockets and HTTP.

The project's build system is Poetry and I'm using Python 3.11 or 3.12. Clone the repo and run `poetry install`.

## Examples with different technologies and frameworks

There are examples for producing and consuming streamed/chunked payloads in several widely used frameworks/libraries: FastAPI, Flask, websockets, urllib3, reactivex.

* Producers/servers:
  * `fastapi`. Demonstrates how to stream upstream server's data or local files. It's in `python_streaming/fastapi_app/app.py`.
  * `flask`. Demonstrates how to stream data coming from an upstream server. It's in `python_streaming/flask_app/app.py`.
  * `websockets`. Demonstrates how to establish a connection and dent data through the `websockets` library. It's in `python_streaming/websockets_app/server.py`.
* **Consumers/clients**:
  * `urllib3`. Demonstrates how to consume a streamed response on the client's side. It's in `python_streaming/chat_client.py`.
  * `reactivex` (RxPy). Demonstrates how to plug a streamed response from a server into a reactive observable, and handle it with further processing. It's in `python_streaming/reactive_client.py`.
  * `websockets`. Using the `websockets` library, the interaction is _not_ processed asynchronously, which is a different concept. It's in `python_streaming/websockets_app/client.py`.
  * `streamlit`. There's an example chatbot application in `python_streaming/streamlit_chat.py`.

## How to run anything

1. Set the environment variables in the `.env` file (you have an `.env.sample` available for reference) 
2. Run the server app you want:
   * FastAPI: `python_streaming/fastapi_app/app.py`
   * Flask: `python_streaming/flask_app/app.py`
   * websockets: `python_streaming/websockets_app/server.py`
3. Invoke each of the different endpoints using your HTTP/WebSockets client of choice (remember _not_ to preload the response). You have a few examples:
   - `python_streaming/chat_client.py` leverages the streamed response
   - `python_streaming/reactive_client.py` provides a demonstration of how to further connect the incoming stream with reactive programming observables
   - `python_streaming/websockets_app/client.py` is a simple, blocking (sync) client for the websockets server

## Upcoming features

Audio _buffering_, deeper frontend client examples, and more!