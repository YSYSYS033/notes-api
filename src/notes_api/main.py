"""notes-api 应用入口。"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from notes_api.db import init_db
from notes_api.routers import notes


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """应用启动时建表。"""
    init_db()
    yield


app = FastAPI(title="notes-api", version="0.1.0", lifespan=lifespan)
app.include_router(notes.router)


@app.get("/health")
def health() -> dict[str, str]:
    """健康检查。"""
    return {"status": "ok"}
