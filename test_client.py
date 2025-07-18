import asyncio
import websockets


async def test():
    uri = "ws://localhost:8000/ws"
    async with websockets.connect(uri) as websocket:
        print("✅ WebSocket connected")

        # 서버로 메시지 보내기
        await websocket.send('{"type": 0}')

        # 서버 응답 받기
        while True:
            msg = await websocket.recv()
            print("📨 Received:", msg)


asyncio.run(test())
