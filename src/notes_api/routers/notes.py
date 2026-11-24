"""笔记相关的路由。"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from notes_api.db import get_db
from notes_api.models import Note
from notes_api.schemas import NoteCreate, NoteRead, NoteUpdate

router = APIRouter(prefix="/notes", tags=["notes"])


@router.post("", response_model=NoteRead, status_code=status.HTTP_201_CREATED)
def create_note(payload: NoteCreate, db: Session = Depends(get_db)) -> Note:
    """新建一条笔记。"""
    note = Note(title=payload.title, content=payload.content)
    db.add(note)
    db.commit()
    db.refresh(note)
    return note


@router.get("", response_model=list[NoteRead])
def list_notes(
    skip: int = Query(default=0, ge=0, description="跳过前 N 条"),
    limit: int = Query(default=20, ge=1, le=100, description="最多返回 N 条"),
    db: Session = Depends(get_db),
) -> list[Note]:
    """分页列出笔记（按 id 升序）。"""
    stmt = select(Note).order_by(Note.id).offset(skip).limit(limit)
    return list(db.scalars(stmt))


# 注意：/search 必须写在 /{note_id} 前面，
# 否则 "search" 会被当成 note_id 去解析，返回 422。
@router.get("/search", response_model=list[NoteRead])
def search_notes(
    q: str = Query(min_length=1, max_length=100, description="标题关键词"),
    db: Session = Depends(get_db),
) -> list[Note]:
    """按标题模糊搜索（不区分大小写）。"""
    stmt = select(Note).where(Note.title.ilike(f"%{q}%")).order_by(Note.id)
    return list(db.scalars(stmt))


@router.get("/{note_id}", response_model=NoteRead)
def get_note(note_id: int, db: Session = Depends(get_db)) -> Note:
    """按 id 查一条笔记，不存在返回 404。"""
    note = db.get(Note, note_id)
    if note is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="笔记不存在")
    return note


@router.patch("/{note_id}", response_model=NoteRead)
def update_note(note_id: int, payload: NoteUpdate, db: Session = Depends(get_db)) -> Note:
    """部分更新：只改请求里出现的字段。"""
    note = db.get(Note, note_id)
    if note is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="笔记不存在")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(note, field, value)
    db.commit()
    db.refresh(note)
    return note


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(note_id: int, db: Session = Depends(get_db)) -> None:
    """删除笔记，成功返回 204，不存在返回 404。"""
    note = db.get(Note, note_id)
    if note is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="笔记不存在")
    db.delete(note)
    db.commit()
