from fastapi import APIRouter, Depends, HTTPException, UploadFile, File

from app.crud import crud_map
from app.schemas.map import MapConfig, MapResponse, MapListResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_db
import os

router = APIRouter()


@router.post("/", response_model=MapResponse, status_code=201)
async def create_map(map_config: MapConfig, db: AsyncSession = Depends(get_db)):
    schema = await crud_map.create_map(map_config, db)
    return MapResponse(type=1101, **schema.model_dump())


@router.post("/upload-image/{map_id}", status_code=201)
async def upload_map_image(map_id: str, file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    existing_map = await crud_map.get_map_by_map_id(map_id, db)
    if not existing_map:
        raise HTTPException(status_code=404, detail="Map not found")

    file_location = existing_map.map_url
    with open(file_location, "wb") as buffer:
        buffer.write(await file.read())

    return {"type": 1105, "map_id": map_id, "file_location": file_location}


@router.get("/", response_model=MapListResponse)
async def get_all_maps(db: AsyncSession = Depends(get_db)):
    schemas = await crud_map.get_all_maps(db)
    return MapListResponse(
        type=1100,
        user_id="all",
        maps=[m for m in schemas]
    )


@router.get("/{user_id}", response_model=MapListResponse)
async def get_maps_by_user(user_id: str, db: AsyncSession = Depends(get_db)):
    schemas = await crud_map.get_all_maps(db)
    return MapListResponse(
        type=1100,
        user_id=user_id,
        maps=[m.model_dump() for m in schemas if m.map_owner_id == user_id]
    )


@router.get("/{map_id}", response_model=MapResponse)
async def get_map_by_map_id(map_id: str, db: AsyncSession = Depends(get_db)):
    schema = await crud_map.get_map_by_map_id(map_id, db)
    if not schema:
        raise HTTPException(status_code=404, detail="Map not found")
    return MapResponse(type=1102, **schema.model_dump())


@router.post("/{map_id}", response_model=MapResponse)
async def update_map(map_id: str, map_config: MapConfig, db: AsyncSession = Depends(get_db)):
    existing_map = await crud_map.get_map_by_map_id(map_id, db)
    if not existing_map:
        raise HTTPException(status_code=404, detail="Map not found")

    updated_map = await crud_map.update_map(map_id, map_config, db)
    return MapResponse(type=1103, **updated_map.model_dump())


@router.delete("/{user_id}/{map_id}", status_code=204)
async def delete_map(user_id: str, map_id: str, db: AsyncSession = Depends(get_db)):
    await crud_map.delete_map(user_id, map_id, db)
    return {"type": 1104, "isRemoved": True}
