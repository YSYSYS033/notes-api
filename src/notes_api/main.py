"""notes-api 应用入口。"""

from fastapi import FastAPI

from notes_api.routers import notes

app = FastAPI(title="notes-api", version="0.1.0")
app.include_router(notes.router)


@app.get("/health")
def health() -> dict[str, str]:
    """健康检查。"""
    return {"status": "ok"}
