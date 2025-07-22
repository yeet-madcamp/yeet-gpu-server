import websockets
import asyncio
import os
import json
from dotenv import load_dotenv

load_dotenv()


async def train_maps(map_ids, test_websocket_path, test_model, stage_name):
    """
    각 맵을 순차적으로 학습.
    episode가 30000을 넘어가도 success==0이면 True 리턴(재학습 필요), 아니면 False 리턴
    """
    need_retrain = False
    for map_id in map_ids:
        url = f"{test_websocket_path}/{test_model}/{map_id}/loop"
        print(f"[{stage_name}] Connecting to {url} ...")
        try:
            async with websockets.connect(url) as websocket:
                await websocket.send("start")
                episode = 0
                success = 0
                while True:
                    message = await websocket.recv()
                    try:
                        msg_json = json.loads(message)
                    except Exception:
                        print("메시지 디코딩 오류:", message)
                        continue

                    # episode, success 값 추출
                    episode = msg_json.get("episode", episode)
                    success = msg_json.get("success", success)
                    print(f"[{map_id}] <{stage_name}> episode: {episode}, success: {success}")

                    # 성공 기준 도달 시 연결 종료
                    if success >= 10000:
                        print(f"{map_id}: success 10000 도달, 연결 종료")
                        await websocket.close()
                        break
                    # 에피소드 3만 초과, 성공 0이면 재학습 플래그
                    if episode >= 30000 and success == 0:
                        print(f"{map_id}: 30000 episode 초과, 성공 없음 -> 재학습 필요")
                        need_retrain = True
                        await websocket.close()
                        break
        except websockets.exceptions.ConnectionClosedOK:
            print("서버가 정상적으로 연결을 종료했습니다.")
        except Exception as e:
            print("예외 발생:", e)
    return need_retrain


async def main():
    test_websocket_path = os.getenv('TEST_WEBSOCKET_PATH')
    test_model = os.getenv('TEST_MODEL')
    test_map_id_easy_list = os.getenv('TEST_MAP_ID_EASY')
    test_map_id_normal_list = os.getenv('TEST_MAP_ID_NORMAL')
    test_map_id_hard_list = os.getenv('TEST_MAP_ID_HARD')

    # 환경 변수는 문자열로 읽히므로, 리스트로 변환 필요
    def parse_ids(s):
        return [x.strip() for x in s.split(',') if x.strip()] if isinstance(s, str) else []

    easy_maps = parse_ids(test_map_id_easy_list)
    normal_maps = parse_ids(test_map_id_normal_list)
    hard_maps = parse_ids(test_map_id_hard_list)

    # easy → normal → hard 순차 진행, 실패 시 전 단계 다시 학습
    while True:
        print("Easy 단계 시작")
        need_easy_retrain = await train_maps(easy_maps, test_websocket_path, test_model, "easy")
        print("Normal 단계 시작")
        need_normal_retrain = await train_maps(normal_maps, test_websocket_path, test_model, "normal")
        print("Hard 단계 시작")
        need_hard_retrain = await train_maps(hard_maps, test_websocket_path, test_model, "hard")

        # 각 단계에서 재학습 필요하면 전 단계로 돌아감
        if need_normal_retrain:
            print("Normal 단계 실패: Easy 맵 재학습 시작")
            continue  # 루프 처음부터 easy부터 다시
        if need_hard_retrain:
            print("Hard 단계 실패: Normal 맵 재학습 시작")
            # easy는 이미 끝났으므로 normal부터 시작
            while True:
                need_normal_retrain = await train_maps(normal_maps, test_websocket_path, test_model, "normal")
                need_hard_retrain = await train_maps(hard_maps, test_websocket_path, test_model, "hard")
                if need_hard_retrain:
                    print("Hard 단계 실패: Normal 맵 재학습 반복")
                    continue
                break
        # 모든 단계 통과 시 종료
        print("모든 단계 통과! 학습 완료")
        break


asyncio.run(main())
