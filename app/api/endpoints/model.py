from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.model import ModelListResponse, ModelResponse, ModelConfig
from app.database.session import get_db
from app.crud import crud_model

router = APIRouter()

@router.get("/user/{user_id}", response_model=ModelListResponse)
async def get_models_by_user_id(user_id: str, db: AsyncSession = Depends(get_db)):
    models = await crud_model.get_all_models(db)
    user_models = [m for m in models if m.model_owner_id == user_id]
    return ModelListResponse(type=1200, models=user_models) if user_models else ModelListResponse(type=1200, models=[])


@router.post("/", response_model=ModelResponse)
async def create_model(model: ModelConfig, db: AsyncSession = Depends(get_db)):
    created_model = await crud_model.create_model(model, db)
    return ModelResponse(type=1201, **created_model.model_dump())


@router.get("/", response_model=ModelListResponse)
async def get_all_models(db: AsyncSession = Depends(get_db)):
    models = await crud_model.get_all_models(db)
    return ModelListResponse(type=1200, models=models)


@router.get("/{model_id}", response_model=ModelResponse)
async def get_model_by_model_id(model_id: str, db: AsyncSession = Depends(get_db)):
    model = await crud_model.get_model_by_model_id(model_id, db)
    return ModelResponse(type=1202, **model.model_dump())


@router.post("/{model_id}", response_model=ModelResponse)
async def update_model(model_id: str, model_config: ModelConfig, db: AsyncSession = Depends(get_db)):
    existing_model = await crud_model.get_model_by_model_id(model_id, db)
    if not existing_model:
        raise HTTPException(status_code=404, detail="Model not found")

    updated_model = await crud_model.update_model(model_id, model_config, db)
    return ModelResponse(type=1203, **updated_model.model_dump())


@router.delete("/{user_id}/{model_id}", status_code=204)
async def delete_model(user_id: str, model_id: str, db: AsyncSession = Depends(get_db)):
    await crud_model.delete_model(user_id, model_id, db)
    return {"type": 1204, "isRemoved": True}
