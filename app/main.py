from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import learning

from app.database.base import Base
from app.database import engine
from dotenv import load_dotenv

load_dotenv()


async def create_db_and_tables():
    """서버 시작 시 데이터베이스에 모든 테이블을 생성합니다."""
    async with engine.begin() as conn:
        # Base.metadata는 models.py에 정의된 모든 테이블 정보를 담고 있습니다.
        await conn.run_sync(Base.metadata.create_all)


app = FastAPI(docs_url='/api/backend/docs')

# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 실제 프로덕션에서는 특정 도메인만 허용하세요.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(learning.router, prefix="/api/backend/learning")


@app.on_event("startup")
async def on_startup():
    # 서버 시작 시 DB 테이블 생성
    await create_db_and_tables()
    # 백그라운드에서 가격 생성기 실행
    # asyncio.create_task(websocket.price_generator())
    # asyncio.create_task(websocket.news_generator())
