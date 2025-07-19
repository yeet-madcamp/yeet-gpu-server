from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import crud_model, crud_map
from app.services.rl_environment import My2DEnv, Size, GridPosition
from app.database.session import get_db

router = APIRouter()


@router.websocket("/learn/{model_id}/{map_id}")
async def websocket_learning_endpoint(websocket: WebSocket, model_id: str, map_id: str,
                                      db: AsyncSession = Depends(get_db)):
    await websocket.accept()

    map_schema = await crud_map.get_map_by_map_id(map_id, db)
    model_schema = await crud_model.get_model_by_model_id(model_id, db)

    if not map_schema:
        await websocket.close(code=4004, reason="Map not found")
        return

    if not model_schema:
        await websocket.close(code=4004, reason="Model not found")
        return

    print(map_schema)
    env = My2DEnv(
        grid_size=Size(map_schema.map_size[0], map_schema.map_size[1]),
        walls=[GridPosition(bit.x, bit.y) for bit in map_schema.bit_list],
        traps=[GridPosition(trap.x, trap.y) for trap in map_schema.trap_list],
        goal=GridPosition(map_schema.exit_pos.x, map_schema.exit_pos.y),
        agent_start=GridPosition(map_schema.agent_pos.x, map_schema.agent_pos.y),
        max_steps=map_schema.max_steps
    )

    try:
        while True:
            state, _ = env.reset()
            await websocket.send_json({"event": "reset", "state": state.tolist()})

            while True:
                data = await websocket.receive_json()
                action = data.get("action")
                if action is None:
                    continue

                state, reward, terminated, truncated, _ = env.step(action)
                await websocket.send_json({
                    "event": "step",
                    "state": state.tolist(),
                    "reward": reward,
                    "done": terminated or truncated
                })
                if terminated or truncated:
                    await websocket.send_json({"event": "episode_end"})
                    break
    except WebSocketDisconnect:
        print(f"Client for map {map_id} disconnected.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        env.close()
