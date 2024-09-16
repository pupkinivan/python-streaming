import json
from typing import Iterator


def iterate_over_json_data() -> Iterator:
    with open('resources/data.json', 'r') as file:
        data = file.read()
    for line in data.splitlines():
        yield line


def iterate_over_audio() -> Iterator:
    with open("resources/audio.mp3", "rb") as file:
        yield from file
