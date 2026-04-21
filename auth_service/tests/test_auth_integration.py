import os
from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

os.environ["SQLITE_PATH"] = "./test_auth.db"

from app.api.deps import get_db
from app.db.base import Base
from app.main import app


DATABASE_URL = "sqlite+aiosqlite:///./test_auth.db"
engine_test = create_async_engine(DATABASE_URL, echo=False)
TestSessionLocal = async_sessionmaker(bind=engine_test, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(autouse=True)
async def prepare_db():
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield


async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    async with TestSessionLocal() as session:
        yield session


app.dependency_overrides[get_db] = override_get_db


@pytest.mark.asyncio
async def test_register_login_me_flow():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        register_resp = await client.post(
            "/auth/register",
            json={"email": "ivanov@email.com", "password": "secret123"},
        )
        assert register_resp.status_code == 201

        login_resp = await client.post(
            "/auth/login",
            data={"username": "ivanov@email.com", "password": "secret123"},
        )
        assert login_resp.status_code == 200
        token = login_resp.json()["access_token"]

        me_resp = await client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert me_resp.status_code == 200
        assert me_resp.json()["email"] == "ivanov@email.com"


@pytest.mark.asyncio
async def test_duplicate_register_returns_409():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        await client.post(
            "/auth/register",
            json={"email": "petrov@email.com", "password": "secret123"},
        )

        resp = await client.post(
            "/auth/register",
            json={"email": "petrov@email.com", "password": "secret123"},
        )
        assert resp.status_code == 409


@pytest.mark.asyncio
async def test_login_wrong_password_returns_401():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        await client.post(
            "/auth/register",
            json={"email": "sidorov@email.com", "password": "secret123"},
        )

        resp = await client.post(
            "/auth/login",
            data={"username": "sidorov@email.com", "password": "wrong"},
        )
        assert resp.status_code == 401


@pytest.mark.asyncio
async def test_me_without_token_returns_401():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/auth/me")
        assert resp.status_code == 401