from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import uuid

from app.schemas.map import MapConfig, MapResponse
from app.models.map import MapModel
from app.services.rl_environment import My2DEnv, GridPosition
from sqlalchemy.ext.asyncio import AsyncSession


router = APIRouter()

# DB 종속성
async def get_db():
    async with SessionLocal() as session:
        yield session

@router.post("/maps", response_model=MapResponse, status_code=201)
async def create_map(map_config: MapConfig, db: AsyncSession = Depends(get_db)):
    map_id = f"map_{uuid.uuid4().hex[:6]}"
    db_map = MapModel(
        id=map_id,
        map_url=map_config.map_url,
        map_name=map_config.map_name,
        map_type=map_config.map_type,
        map_owner_id=map_config.map_owner_id,
        map_owner_name=map_config.map_owner_name,
        map_size=list(map_config.map_size),
        agent_pos=list(map_config.agent_pos),
        exit_pos=list(map_config.exit_pos),
        bit_list=map_config.bit_list,
        trap_list=map_config.trap_list,
        max_steps=map_config.max_steps
    )
    db.add(db_map)
    await db.commit()
    return MapResponse(map_id=map_id, **map_config.dict())

@router.get("/maps", response_model=List[MapResponse])
async def get_all_maps(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(MapModel))
    maps = result.scalars().all()
    return [
        MapResponse(
            map_id=m.id,
            map_url=m.map_url,
            map_name=m.map_name,
            map_type=m.map_type,
            map_owner_id=m.map_owner_id,
            map_owner_name=m.map_owner_name,
            map_size=tuple(m.map_size),
            agent_pos=tuple(m.agent_pos),
            exit_pos=tuple(m.exit_pos),
            bit_list=m.bit_list,
            trap_list=m.trap_list,
            max_steps=m.max_steps
        ) for m in maps
    ]

@router.get("/maps/{map_id}", response_model=MapResponse)
async def get_map_by_id(map_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(MapModel).where(MapModel.id == map_id))
    m = result.scalar_one_or_none()
    if not m:
        raise HTTPException(status_code=404, detail="Map not found")
    return MapResponse(
        map_id=m.id,
        map_url=m.map_url,
        map_name=m.map_name,
        map_type=m.map_type,
        map_owner_id=m.map_owner_id,
        map_owner_name=m.map_owner_name,
        map_size=tuple(m.map_size),
        agent_pos=tuple(m.agent_pos),
        exit_pos=tuple(m.exit_pos),
        bit_list=m.bit_list,
        trap_list=m.trap_list,
        max_steps=m.max_steps
    )

@router.websocket("/ws/learn/{map_id}")
async def websocket_learning_endpoint(websocket: WebSocket, map_id: str):
    await websocket.accept()

    async with SessionLocal() as db:
        result = await db.execute(select(MapModel).where(MapModel.id == map_id))
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
