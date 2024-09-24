from math import ceil
from pathlib import Path
from pprint import pprint
import re
from typing import Iterator, Generator, AsyncIterator
import wave

import pyaudio
import soundfile as sf

from python_streaming.config import BUFFER_SIZE, RANGED_REQUEST_BUFFERS


def extract_bit_depth(file_info_string: str):
    pattern = r"Bit Width\s*:\s*(\d+)"
    if matches := re.findall(pattern, file_info_string):
        return int(matches[0])
    return None


def frames_to_bytes(frames: int, bit_depth: int, channels: int):
    """Converts a number of frames to a number bytes corresponding to the
    provided WAVE file information."""
    return (
        frames
        * channels
        * (bit_depth // 8)
    )


def read_audio_frames(audio_file_path: Path, start_frame: int, frames: int):
    header_size = 44
    audio_info = sf.info(audio_file_path)
    start_byte = (
        header_size
        + frames_to_bytes(
            start_frame,
            extract_bit_depth(audio_info.extra_info),
            audio_info.channels,
        )
    )
    end_byte = (
        start_byte
        + frames_to_bytes(
            frames,
            extract_bit_depth(audio_info.extra_info),
            audio_info.channels,
        )
    )
    pprint(f"Reading bytes {start_byte} to {end_byte}")

    with open(audio_file_path, "rb") as audio:
        audio.seek(start_byte)
        data = audio.read(end_byte - start_byte)
        return data


def read_wav_frames(audio_file_path: Path, start_frame: int, n_frames: int):
        with wave.open(str(audio_file_path), "rb") as audio:
            audio.setpos(start_frame)
            data = audio.readframes(n_frames)
        return data


def iterate_over_wav_frames(audio_file_path: Path) -> Generator:
    start_frame = 0
    while True:
        data = read_wav_frames(audio_file_path, start_frame, BUFFER_SIZE)
        start_frame += BUFFER_SIZE
        if not data:
            raise ValueError("No more data to read")
        yield data


def create_audio_iterator(audio_file_path: Path) -> Iterator:
    # file_info = sf.info(str(audio_file_path))
    # assert file_info.format == "WAV", "Only WAV files are supported for this type of iterator!"
    import wave

    audio_file = wave.open(str(audio_file_path), "rb")
    while len(data := audio_file.readframes(BUFFER_SIZE)) > 0:
        yield data

    # soundfile stuff
    # It's not well documented how PyAudio and wave handle the sample bytes, so plugging soundfile needs figuring out
    #
    # number_of_buffers = ceil(file_info.frames / BUFFER_SIZE)
    # for i in range(number_of_buffers):
    #     if i == number_of_buffers:
    #         audio_signal, _ = sf.read(audio_file_path, start=i*BUFFER_SIZE)
    #         yield audio_signal
    #         break
    #     audio_signal, _ = sf.read(audio_file_path, start=i*BUFFER_SIZE, frames=BUFFER_SIZE)
    #     yield audio_signal

    # print(
    #     f"Frames: {file_info.frames}\n"
    #     f"\tDuration: {file_info.duration}\n"
    #     f"\tChannels: {file_info.channels}"
    #     f"\tSample rate: {file_info.samplerate}\n"
    #     f"\t{file_info.extra_info = }\n"
    #     f"\t{file_info.subtype = }\n"
    #     f"\t{file_info.subtype_info = }\n"
    #     f"\t{file_info.sections = }\n"
    #     f"\t{file_info.endian = }\n"
    # )
    # print(type(file_info.extra_info))
    # print(file_info.extra_info)

    # This or...
    # stream = pya.Stream(
    #     channels=file_info.channels,
    #     rate=file_info.samplerate,
    #     format=file_info
    # )

    # ... or that
    # stream = pya.open(
    #     format=pya.get_format_from_width(extract_bit_depth(file_info.extra_info)//8),
    #     channels=file_info.channels,
    #     rate=file_info.samplerate,
    #     input=True,
    #     frames_per_buffer=BUFFER_SIZE
    # )


async def play_sound_from_iterator(
    audio_data_iterator: Iterator[bytes] | AsyncIterator[bytes],
    output_file_path: Path,
    bit_depth: int,
    number_of_channels: int,
    sample_rate: int,
    buffer_size: int
):
    # PyAudio stream setup
    pya = pyaudio.PyAudio()

    # ... or that
    stream = pya.open(
        format=pya.get_format_from_width(bit_depth//8),
        channels=number_of_channels,
        rate=sample_rate,
        output=True,
        frames_per_buffer=buffer_size
    )

    if isinstance(audio_data_iterator, Iterator):
        while (audio_data := next(audio_data_iterator)) is not None:
            stream.write(audio_data, num_frames=buffer_size, exception_on_underflow=False)
            with open(output_file_path, "ab") as file:
                file.write(audio_data)
    elif isinstance(audio_data_iterator, AsyncIterator):
        while (audio_data := await anext(audio_data_iterator)) is not None:
            stream.write(audio_data, num_frames=buffer_size, exception_on_underflow=False)
            with open(output_file_path, "ab") as file:
                file.write(audio_data)
    else:
        raise ValueError("Unsupported iterator type")

    stream.close()
    pya.terminate()


def audio_stream():
    import pickle
    import os
    import struct
    import socket
    host_ip, port = "192.0.0.1", 8080
    p = pyaudio.PyAudio()
    CHUNK = 1024
    stream = p.open(format=p.get_format_from_width(2),
                    channels=2,
                    rate=44100,
                    output=True,
                    frames_per_buffer=CHUNK)

    # create socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_address = (host_ip, port - 1)
    print('server listening at', socket_address)
    client_socket.connect(socket_address)
    print("CLIENT CONNECTED TO", socket_address)
    data = b""
    payload_size = struct.calcsize("Q")
    while True:
        try:
            while len(data) < payload_size:
                packet = client_socket.recv(4 * 1024)  # 4K
                if not packet: break
                data += packet
            packed_msg_size = data[:payload_size]
            data = data[payload_size:]
            msg_size = struct.unpack("Q", packed_msg_size)[0]
            while len(data) < msg_size:
                data += client_socket.recv(4 * 1024)
            frame_data = data[:msg_size]
            data = data[msg_size:]
            frame = pickle.loads(frame_data)
            stream.write(frame)

        except:

            break

    client_socket.close()
    print('Audio closed')
    os._exit(1)


if __name__ == '__main__':
    # audio_iterator = create_audio_iterator(Path("resources/audio.wav"))
    # consume_wave_file(
    #     audio_data_iterator=audio_iterator,
    #     output_file_path=Path("resources/audio_output.wav"),
    #     bit_depth=16,
    #     number_of_channels=2,
    #     sample_rate=44100,
    #     buffer_size=8192
    # )

    # from sys import byteorder
    # with open("resources/audio.wav", "rb") as file:
    #     file.seek(24)
    #     data = file.read(4)
    #     data = int.from_bytes(data, byteorder)
    #     print(data)

    audio_path = Path("resources/audio.wav")
    file_info = sf.info(audio_path)
    iterator = iterate_over_wav_frames(audio_path)

    play_sound_from_iterator(
        audio_data_iterator=iterator,
        output_file_path=Path("resources/audio_output.wav"),
        bit_depth=extract_bit_depth(file_info.extra_info),
        number_of_channels=file_info.channels,
        sample_rate=file_info.samplerate,
        buffer_size=BUFFER_SIZE*RANGED_REQUEST_BUFFERS
    )
