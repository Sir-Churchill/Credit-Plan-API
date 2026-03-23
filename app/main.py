import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from app.reader import upload
from app.routes import router
from app.database import engine
from app.models import Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    try:
        await upload()
    except Exception as e:
        logging.info(f"Помилка автоімпорту при старті: {e}")
    yield


app = FastAPI(
    title="Credit Plan API",
    description="Система управління планами та аналітики кредитів",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(router, tags=["v1"])

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000, reload=True)