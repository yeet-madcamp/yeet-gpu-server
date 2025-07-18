from fastapi import FastAPI, WebSocket
from gym.envs.registration import register
import gym
import json

app = FastAPI()
register(
    id='MyEnv-v0',
    entry_point='2d_env:My2DEnv',
)

env = gym.make("MyEnv-v0")


@app.websocket("/ws")
async def rl_ws_endpoint(websocket: WebSocket):
    await websocket.accept()

    while True:
        data = await websocket.receive_text()
        type = json.loads(data).get("type")

        if type == 0:
            print("Received type 0, websocket connection success")
            continue
        elif type == 1:
            print("Received type 1, disconnect success")
            await websocket.close()
            continue
        elif type == 1100:
            print("Received type 1100, load maps with id:", json.loads(data).get("user_id"))
            continue
        elif type == 1101:
            print("Received type 1101, create map with id:", json.loads(data).get("user_id"))
            continue
        elif type == 1102:
            print("Received type 1102, read map with id:", json.loads(data).get("user_id"))
            continue
        elif type == 1103:
            print("Received type 1103, update map with id:", json.loads(data).get("user_id"))
            continue
        elif type == 1104:
            print("Received type 1104, delete map with id:", json.loads(data).get("user_id"))
            continue
        elif type == 1200:
            print("Received type 1200, load models with id:", json.loads(data).get("user_id"))
            continue
        elif type == 4000:
            print("Received type 4000, ", json.loads(data).get("user_id"), " start learning model_id:",
                  json.loads(data).get("model_id"))
            continue
        elif type == 4001:
            print("Received type 4001, ", json.loads(data).get("user_id"), " stop learning model_id:",
                  json.loads(data).get("model_id"))
            continue

    # obs, result = env.reset()
    # done = False
    #
    # while not done:
    #     action = env.action_space.sample()
    #     next_obs, reward, done, _, _ = env.step(action)
    #
    #     await websocket.send_text(json.dumps({
    #         "state": next_obs.tolist(),
    #         "reward": reward,
    #         "done": done
    #     }))
    #     obs = next_obs
