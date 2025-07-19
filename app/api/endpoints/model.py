from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.model import ModelListResponse
from app.database.session import get_db
from app.crud import crud_model

router = APIRouter()


@router.get("/{user_id}", response_model=ModelListResponse)
async def get_models_by_user_id(user_id: str, db: AsyncSession = Depends(get_db)):
    models = await crud_model.get_all_models(db)
    user_models = [m for m in models if m.model_owner_id == user_id]
    return ModelListResponse(type=1200, models=user_models) if user_models else ModelListResponse(type=1200, models=[])
