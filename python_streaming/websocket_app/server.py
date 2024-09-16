import asyncio
import websockets

from python_streaming.util import iterate_over_json_data


async def stream_json_data(websocket):
    async for message in websocket:
        if message != "json":
            print(f"Received message: {message}")
            await websocket.send(f"Echoing message: {message}")
        else:
            print("Asked for JSON...")
            data_iterator = iterate_over_json_data()
            try:
                while new_line := next(data_iterator):
                    await asyncio.sleep(0.05)
                    print(f"New data chunk: {new_line}")
                    await websocket.send(new_line)
            except StopIteration:
                pass
        await websocket.send("EOF")
        # await websocket.close()


async def main():
    server = await websockets.serve(stream_json_data, "localhost", 8765)
    print("WebSocket server started")
    await server.wait_closed()


if __name__ == "__main__":
    asyncio.run(main())
