import asyncio
import websockets


async def test():
    uri = "ws://localhost:8000/api/backend/ws/learn/model_24eda0/map_2a63df"
    async with websockets.connect(uri) as websocket:
        print("✅ WebSocket connected")

        # 서버 응답 받기
        while True:
            msg = await websocket.recv()
            print("📨 Received:", msg)
            await websocket.send(
                '{"action": 0, "state": []}'
            )


asyncio.run(test())
