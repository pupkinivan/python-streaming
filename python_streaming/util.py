import json
from typing import Iterator

import boto3
from botocore.exceptions import ClientError


def iterate_over_json_data() -> Iterator:
    with open('resources/data.json', 'r') as file:
        data = file.read()
    for line in data.splitlines():
        yield line


def iterate_over_audio() -> Iterator:
    with open("resources/audio.mp3", "rb") as file:
        yield from file


def download_s3_object_streaming(
    object_key: str,
    bucket_name: str,
    chunk_size: int = 1024
) -> Iterator:
    s3 = boto3.resource('s3')
    try:
        s3_object = s3.Object(bucket_name, object_key)
        streaming_body = s3_object.get()['Body']

        for chunk in iter(lambda: streaming_body.read(chunk_size), b''):
            yield chunk
    except ClientError as e:
        print(f"Error streaming object from S3: {e}")
        yield None
