from flask import Flask, request

from python_streaming import chatting_service

app = Flask("Flask streaming")


@app.post("/chat")
async def chat():
    if request.content_type != "application/json":
        return "Only JSON data is accepted.", 415
    user_message = request.get_json()["message"]
    # The chatting service exposes a generator that iterates over Bedrock response events
    bedrock_streaming_response = await chatting_service.chat(user_message)
    return app.response_class(bedrock_streaming_response, content_type="text/plain")