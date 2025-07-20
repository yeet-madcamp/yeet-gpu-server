import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.map import MapModel
from app.schemas.map import MapConfig, MapSchema
from sqlalchemy.future import select
from fastapi import HTTPException


async def create_map(map_config: MapConfig, db: AsyncSession):
    map_id = f"map_{uuid.uuid4().hex[:6]}"
    map_url = f"https://example.com/maps/{map_id}.png"  # Placeholder URL, replace with actual logic if needed
    db_map = MapModel(
        map_id=map_id,
        map_url=map_url,
        map_name=map_config.map_name,
        map_type=map_config.map_type,
        map_owner_id=map_config.map_owner_id,
        map_owner_name=map_config.map_owner_name,
        map_size=map_config.map_size,
        agent_pos=map_config.agent_pos.model_dump(),
        exit_pos=map_config.exit_pos.model_dump(),
        wall_list=[pos.model_dump() for pos in map_config.wall_list],
        bit_list=[pos.model_dump() for pos in map_config.bit_list],
        trap_list=[pos.model_dump() for pos in map_config.trap_list],
        max_steps=map_config.max_steps
    )
    db.add(db_map)
    await db.commit()
    return MapSchema(**map_config.model_dump(), map_id=map_id, map_url=map_url)


async def get_all_maps(db: AsyncSession):
    result = await db.execute(select(MapModel))
    maps = result.scalars().all()
    return [
        MapSchema(
            map_id=m.map_id,
            map_url=m.map_url,
            map_name=m.map_name,
            map_type=m.map_type,
            map_owner_id=m.map_owner_id,
            map_owner_name=m.map_owner_name,
            map_size=m.map_size,
            agent_pos=m.agent_pos,
            exit_pos=m.exit_pos,
            wall_list=m.wall_list,
            bit_list=m.bit_list,
            trap_list=m.trap_list,
            max_steps=m.max_steps
        ) for m in maps
    ]


async def get_map_by_map_id(map_id: str, db: AsyncSession):
    result = await db.execute(select(MapModel).where(MapModel.map_id == map_id))
    m = result.scalar_one_or_none()
    if not m:
        raise HTTPException(status_code=404, detail="Map not found")
    return MapSchema(
        map_id=m.map_id,
        map_url=m.map_url,
        map_name=m.map_name,
        map_type=m.map_type,
        map_owner_id=m.map_owner_id,
        map_owner_name=m.map_owner_name,
        map_size=m.map_size,
        agent_pos=m.agent_pos,
        exit_pos=m.exit_pos,
        wall_list=m.wall_list,
        bit_list=m.bit_list,
        trap_list=m.trap_list,
        max_steps=m.max_steps
    )


async def update_map(map_id: str, map_config: MapConfig, db: AsyncSession):
    existing_map = await get_map_by_map_id(map_id, db)

    if not existing_map:
        raise HTTPException(status_code=404, detail="Map not found")

    updated_map = MapModel(
        map_id=map_id,
        map_url=existing_map.map_url,
        map_name=map_config.map_name,
        map_type=map_config.map_type,
        map_owner_id=map_config.map_owner_id,
        map_owner_name=map_config.map_owner_name,
        map_size=map_config.map_size,
        agent_pos=map_config.agent_pos.model_dump(),
        exit_pos=map_config.exit_pos.model_dump(),
        wall_list=[pos.model_dump() for pos in map_config.wall_list],
        bit_list=[pos.model_dump() for pos in map_config.bit_list],
        trap_list=[pos.model_dump() for pos in map_config.trap_list],
        max_steps=map_config.max_steps
    )

    await db.merge(updated_map)
    await db.commit()
    return MapSchema(map_id=map_id, map_url=updated_map.map_url, **map_config.model_dump())


async def delete_map(user_id: str, map_id: str, db: AsyncSession):
    print(f"Deleting map with ID: {map_id} for user: {user_id}")
    target = await db.get(MapModel, map_id)

    if not target:
        raise HTTPException(status_code=404, detail="Map not found")
    if target.map_owner_id != user_id:
        raise HTTPException(status_code=403, detail="You do not have permission to delete this map")

    await db.delete(target)
    await db.commit()
    return {"detail": "Map deleted successfully"}
