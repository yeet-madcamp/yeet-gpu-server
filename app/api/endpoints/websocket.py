from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.rl_environment import My2DEnv, GridPosition
from sqlalchemy.future import select
from app.models.map import MapModel

router = APIRouter()


@router.websocket("/ws/learn/{map_id}")
async def websocket_learning_endpoint(websocket: WebSocket, map_id: str):
    await websocket.accept()

    async with AsyncSession() as db:
        result = await db.execute(select(MapModel).where(MapModel.map_id == map_id))
        m = result.scalar_one_or_none()

    if not m:
        await websocket.close(code=4004, reason="Map not found")
        return

    env = My2DEnv(
        grid_size=GridPosition(*m.map_size),
        walls=m.bit_list,
        traps=m.trap_list,
        goal=m.exit_pos,
        agent_start=GridPosition(*m.agent_pos),
        max_steps=m.max_steps
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
