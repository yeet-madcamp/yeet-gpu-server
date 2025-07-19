from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
import uuid

from app.schemas.model import Position, ModelSchema, ModelConfig
from app.models.model import Model


async def get_all_models(db: AsyncSession):
    result = await db.execute(select(Model))
    models = result.scalars().all()

    return [ModelSchema(
        model_id=m.model_id,
        model_url=m.model_url,
        model_owner_id=m.model_owner_id,
        model_owner_name=m.model_owner_name,
        model_name=m.model_name,
        model_type=m.model_type,
        learning_rate=m.learning_rate,
        batch_size=Position(**m.batch_size),
        n_steps=m.n_steps,
        n_epochs=m.n_epochs,
    )
        for m in models]


async def get_model_by_model_id(model_id: str, db: AsyncSession):
    result = await db.execute(select(Model).where(Model.model_id == model_id))
    m = result.scalar_one_or_none()
    if not m:
        raise HTTPException(status_code=404, detail="Model not found")
    return ModelSchema(
        model_id=m.model_id,
        model_url=m.model_url,
        model_owner_id=m.model_owner_id,
        model_owner_name=m.model_owner_name,
        model_name=m.model_name,
        model_type=m.model_type,
        learning_rate=m.learning_rate,
        batch_size=Position(**m.batch_size),
        n_steps=m.n_steps,
        n_epochs=m.n_epochs
    )


async def create_model(model_config: ModelConfig, db: AsyncSession):
    model_id = f"model_{uuid.uuid4().hex[:6]}"
    model_url = f"https://example.com/models/{model_id}.zip"  # Placeholder URL, replace with actual logic if needed
    db_model = Model(
        model_id=model_id,
        model_url=model_url,
        model_owner_id=model_config.model_owner_id,
        model_owner_name=model_config.model_owner_name,
        model_name=model_config.model_name,
        model_type=model_config.model_type,
        learning_rate=model_config.learning_rate,
        batch_size=model_config.batch_size.model_dump(),
        n_steps=model_config.n_steps,
        n_epochs=model_config.n_epochs
    )
    db.add(db_model)
    await db.commit()

    return ModelSchema(**model_config.model_dump(), model_id=model_id, model_url=model_url)


async def update_model(model_id: str, model_config: ModelConfig, db: AsyncSession):
    existing_model = await get_model_by_model_id(model_id, db)

    if not existing_model:
        raise HTTPException(status_code=404, detail="Model not found")

    updated_model = Model(
        model_id=model_id,
        model_url=existing_model.model_url,  # Assuming URL remains unchanged
        model_owner_id=model_config.model_owner_id,
        model_owner_name=model_config.model_owner_name,
        model_name=model_config.model_name,
        model_type=model_config.model_type,
        learning_rate=model_config.learning_rate,
        batch_size=model_config.batch_size.model_dump(),
        n_steps=model_config.n_steps,
        n_epochs=model_config.n_epochs
    )

    await db.merge(updated_model)
    await db.commit()
    return ModelSchema(model_id=model_id, model_url=updated_model.model_url, **model_config.model_dump())


async def delete_model(user_id:str, model_id: str, db: AsyncSession):
    print(f"Deleting model with ID: {model_id} for user: {user_id}")
    target = await db.get(Model, model_id)

    if not target:
        raise HTTPException(status_code=404, detail="Model not found")
    if target.model_owner_id != user_id:
        raise HTTPException(status_code=403, detail="You do not have permission to delete this model")

    await db.delete(target)
    await db.commit()
    return {"detail": "Model deleted successfully"}
