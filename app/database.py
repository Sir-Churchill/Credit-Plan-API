import os

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base

load_dotenv()

user = os.environ.get("user")
password = os.environ.get("password")
host = os.environ.get("host")
db = os.environ.get("db")

MYSQL_ENGINE_URL = f"mysql+aiomysql://{user}:{password}@{host}/{db}"

engine = create_async_engine(MYSQL_ENGINE_URL, echo=True)

AsyncSessionLocal = async_sessionmaker(
    bind=engine, expire_on_commit=False, class_=AsyncSession
)

Base = declarative_base()


async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session
