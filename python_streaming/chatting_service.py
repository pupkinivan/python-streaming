import asyncio
import json
from typing import Iterable

import boto3


async def chat(user_message: str):
    def extract_chunk_from_body(response_body: Iterable):
        for event in response_body:
            chunk = json.loads(event["chunk"]["bytes"])
            if chunk["type"] == "content_block_delta":
                text: str = chunk["delta"].get("text", "")
                yield chunk["delta"].get("text", "")
    bedrock = boto3.client("bedrock-runtime")
    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 512,
        "temperature": 0.5,
        "messages": [
            {
                "role": "user",
                "content": [{"type": "text", "text": user_message}],
            },
        ],
    }
    body = json.dumps(body)
    response = bedrock.invoke_model_with_response_stream(
        body=body,
        contentType="application/json",
        accept="application/json",
        modelId="anthropic.claude-3-haiku-20240307-v1:0"
    )
    return extract_chunk_from_body(response["body"])
