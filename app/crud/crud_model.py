from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

from app.schemas.model import ModelListResponse, ModelResponse, Position, ModelSchema
from app.models.model import Model


async def get_all_models(db: AsyncSession):
    result = await db.execute(select(Model))
    models = result.scalars().all()

    return [ModelSchema(
        model_id=m.id,
        model_url=m.url,
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
