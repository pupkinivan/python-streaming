import asyncio
import websockets


async def chat_with_server():
    uri = "ws://localhost:8765"
    async with websockets.connect(uri) as websocket:
        while True:
            message = input("Enter a message (or 'quit' to exit): ")
            if message.lower() == 'quit':
                break
            await websocket.send(message)
            while (response := await websocket.recv()) != "EOF":
                # websocket.eof_received()
                print(f"Received: {response}")


if __name__ == "__main__":
    asyncio.run(chat_with_server())
