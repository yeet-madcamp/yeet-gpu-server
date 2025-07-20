from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import uuid
import os

from app.schemas.model import ModelSchema, ModelConfig
from app.models.model import Model


async def get_all_models(db: AsyncSession):
    result = await db.execute(select(Model))
    models = result.scalars().all()

    return [ModelSchema.from_model(m)
            for m in models]


async def get_model_by_model_id(model_id: str, db: AsyncSession):
    result = await db.execute(select(Model).where(Model.model_id == model_id))
    m = result.scalar_one_or_none()
    if not m:
        raise HTTPException(status_code=404, detail="Model not found")
    return ModelSchema.from_model(m)


async def create_model(model_config: ModelConfig, db: AsyncSession):
    model_id = f"model_{uuid.uuid4().hex[:6]}"
    model_url = f"{os.getenv('MODEL_PATH')}/{model_id}.pth"  # Placeholder URL, replace with actual logic if needed
    db_model = Model.from_model_config(
        model_id=model_id,
        model_url=model_url,
        config=model_config,
    )
    db.add(db_model)
    await db.commit()

    return ModelSchema(**model_config.model_dump(), model_id=model_id, model_url=model_url)


async def update_model(model_id: str, model_config: ModelConfig, db: AsyncSession):
    existing_model = await get_model_by_model_id(model_id, db)

    if not existing_model:
        raise HTTPException(status_code=404, detail="Model not found")

    updated_model = Model.from_model_config(
        model_id=model_id,
        model_url=existing_model.model_url,
        config=model_config,
    )

    await db.merge(updated_model)
    await db.commit()
    return ModelSchema(model_id=model_id, model_url=updated_model.model_url, **model_config.model_dump())


async def delete_model(user_id: str, model_id: str, db: AsyncSession):
    print(f"Deleting model with ID: {model_id} for user: {user_id}")
    target = await db.get(Model, model_id)

    if not target:
        raise HTTPException(status_code=404, detail="Model not found")
    if target.model_owner_id != user_id:
        raise HTTPException(status_code=403, detail="You do not have permission to delete this model")

    await db.delete(target)
    await db.commit()
    return {"detail": "Model deleted successfully"}
