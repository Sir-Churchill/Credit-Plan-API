import asyncio

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.models import Base
from app.database import engine
import pandas as pd
from io import BytesIO


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture(scope="function", autouse=True)
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()

@pytest_asyncio.fixture(scope="function")
async def db_session():
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session

@pytest_asyncio.fixture(scope="function")
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_plans_insert_wrong_date(client):
    data = {"sum": [100], "period": ["2026-03-15"], "category": ["видача"]}
    file = BytesIO()
    pd.DataFrame(data).to_excel(file, index=False)
    file.seek(0)

    response = await client.post(
        "/plans_insert",
        files={"plans_insert": ("test.xlsx", file, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
    )

    assert response.status_code == 400
    assert "must start on the 1st day" in response.json()["detail"]


@pytest.mark.asyncio
async def test_get_user_credits_not_found(client):
    response = await client.get("/user_credits/99999")

    assert response.status_code == 404
    assert "User not found" in response.json()["detail"]


@pytest.mark.asyncio
async def test_get_user_credits_empty_list(client):
    response = await client.get("/user_credits/1")

    if response.status_code == 200:
        assert response.json() == []


@pytest.mark.asyncio
async def test_plans_insert_invalid_file_type(client):
    file_content = b"this is not an excel file"
    response = await client.post(
        "/plans_insert",
        files={"plans_insert": ("test.txt", file_content, "text/plain")}
    )

    assert response.status_code == 400
    assert "Invalid Excel" in response.json()["detail"]

@pytest.mark.asyncio
async def test_get_user_credits_wrong_id_type(client):
    response = await client.get("/user_credits/abc")

    assert response.status_code == 422

    error_msg = response.json()["detail"][0]["msg"]

    assert "integer" in error_msg.lower()

@pytest.mark.asyncio
async def test_plans_insert_empty_dataframe(client):
    df = pd.DataFrame(columns=["sum", "period", "category"])
    file = BytesIO()
    df.to_excel(file, index=False)
    file.seek(0)

    response = await client.post(
        "/plans_insert",
        files={"plans_insert": ("empty.xlsx", file, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
    )

    assert response.status_code == 400
    assert "The file is empty" in response.json()["detail"]

@pytest.mark.asyncio
async def test_plans_insert_missing_columns(client):
    data = {"period": ["2026-03-01"], "category": ["видача"]}
    file = BytesIO()
    pd.DataFrame(data).to_excel(file, index=False)
    file.seek(0)

    response = await client.post(
        "/plans_insert",
        files={"plans_insert": ("missing_cols.xlsx", file, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
    )

    assert response.status_code == 400
    assert "Missing columns" in response.json()["detail"]