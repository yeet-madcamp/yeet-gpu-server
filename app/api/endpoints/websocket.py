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

    env = My2DEnv(
        grid_size=Size(map_schema.map_size[0], map_schema.map_size[1]),
        walls=[GridPosition(bit.x, bit.y) for bit in map_schema.bit_list],
        traps=[GridPosition(trap.x, trap.y) for trap in map_schema.trap_list],
        goal=GridPosition(map_schema.exit_pos.x, map_schema.exit_pos.y),
        agent_start=GridPosition(map_schema.agent_pos.x, map_schema.agent_pos.y),
        max_steps=map_schema.max_steps
    )
    try:
        while True:  # 전체 에피소드 반복
            state, _ = env.reset()
            await websocket.send_json({"event": "reset", "state": state.tolist()})

            done = False
            while not done:
                action = env.action_space.sample()
                state, reward, terminated, truncated, _ = env.step(action)
                env.render()
                await websocket.send_json({
                    "event": "step",
                    "steps": env.current_step,
                    "state": state.tolist(),
                    "reward": reward,
                    "terminated": terminated,
                    "truncated": truncated
                })
                done = terminated or truncated

            await websocket.send_json({"event": "episode_end"})
    except WebSocketDisconnect:
        print(f"Client for map {map_id} disconnected.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        env.close()
