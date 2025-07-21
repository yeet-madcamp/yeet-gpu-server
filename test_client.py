import websockets
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()
async def test():
    async with websockets.connect(f"{os.getenv('TEST_WEBSOCKET_PATH')}") as websocket:
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