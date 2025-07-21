import websockets
import asyncio

async def test():
    async with websockets.connect("ws://localhost:8000/api/backend/ws/train_dqn/model_6b088d/map_74fbc6") as websocket:
        try:
            await websocket.send("start")
            async for message in websocket:
                # 처리
                print(message)
        except websockets.exceptions.ConnectionClosedOK:
            print("서버가 정상적으로 연결을 종료했습니다.")
        except Exception as e:
            print("예외 발생:", e)

asyncio.run(test())