"""Pydantic 模型：请求体和响应体的结构定义。"""

from datetime import datetime

from pydantic import BaseModel, Field


class NoteCreate(BaseModel):
    """创建笔记的请求体。"""

    title: str = Field(min_length=1, max_length=200, description="标题")
    content: str = Field(default="", max_length=10000, description="正文")


class NoteUpdate(BaseModel):
    """更新笔记的请求体：所有字段可选，只改传了的字段。"""

    title: str | None = Field(default=None, min_length=1, max_length=200)
    content: str | None = Field(default=None, max_length=10000)


class NoteRead(BaseModel):
    """返回给客户端的笔记结构。"""

    model_config = {"from_attributes": True}

    id: int
    title: str
    content: str
    created_at: datetime
