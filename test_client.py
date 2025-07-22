import websockets
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()
async def test():
    test_websocket_path = os.getenv('TEST_WEBSOCKET_PATH')
    test_model = os.getenv('TEST_MODEL')

    while True:
        async with websockets.connect(f"{test_websocket_path}/{test_model}") as websocket:
            try:
                await websocket.send("start")
                async for message in websocket:
                    print(message)

            except websockets.exceptions.ConnectionClosedOK:
                print("서버가 정상적으로 연결을 종료했습니다.")
            except Exception as e:
                print("예외 발생:", e)

asyncio.run(test())