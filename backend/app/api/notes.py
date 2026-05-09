"""便签接口 - 增删改查、颜色更新、置顶切换"""
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.family import Note, User
from app.api.deps import get_current_user

router = APIRouter()
limiter = Limiter(key_func=get_remote_address, default_limits=[])


class NoteCreate(BaseModel):
    title: str | None = Field(default=None, max_length=200)
    content: str = Field(default="", max_length=10000)
    color: str = Field(default="#FFE066", max_length=7)


class NoteUpdate(BaseModel):
    title: str | None = Field(default=None, max_length=200)
    content: str | None = Field(default=None, max_length=10000)
    color: str | None = Field(default=None, max_length=7)
    pinned: bool | None = None


def _note_dict(n: Note) -> dict:
    return {
        "id": n.id,
        "family_id": n.family_id,
        "title": n.title,
        "content": n.content,
        "color": n.color,
        "pinned": n.pinned,
        "created_at": n.created_at.isoformat() if n.created_at else None,
        "updated_at": n.updated_at.isoformat() if n.updated_at else None,
    }


@router.get("/")
async def list_notes(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取便签列表 - 置顶优先，然后按更新时间倒序"""
    if not user.member:
        raise HTTPException(403, "当前用户未关联家庭成员")
    family_id = user.member.family_id

    result = await db.execute(
        select(Note)
        .where(Note.family_id == family_id)
        .order_by(Note.pinned.desc(), Note.updated_at.desc())
    )
    notes = result.scalars().all()
    return [_note_dict(n) for n in notes]


@router.post("/")
@limiter.limit("30/minute")
async def create_note(
    request: Request,
    note: NoteCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """创建便签"""
    if not user.member:
        raise HTTPException(403, "当前用户未关联家庭成员")
    family_id = user.member.family_id

    new_note = Note(
        family_id=family_id,
        title=note.title,
        content=note.content,
        color=note.color,
    )
    db.add(new_note)
    await db.commit()
    await db.refresh(new_note)
    return _note_dict(new_note)


@router.patch("/{note_id}")
async def update_note(
    note_id: int,
    note: NoteUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """更新便签 - 可更新内容、颜色、置顶状态"""
    if not user.member:
        raise HTTPException(403, "当前用户未关联家庭成员")
    family_id = user.member.family_id

    result = await db.execute(
        select(Note).where(Note.id == note_id, Note.family_id == family_id)
    )
    existing = result.scalar_one_or_none()
    if not existing:
        raise HTTPException(404, "便签不存在")

    update_data = note.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(existing, field, value)

    # 自动更新 updated_at 时间戳
    existing.updated_at = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(existing)
    return _note_dict(existing)


@router.delete("/{note_id}")
async def delete_note(
    note_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """删除便签"""
    if not user.member:
        raise HTTPException(403, "当前用户未关联家庭成员")
    family_id = user.member.family_id

    result = await db.execute(
        select(Note).where(Note.id == note_id, Note.family_id == family_id)
    )
    existing = result.scalar_one_or_none()
    if not existing:
        raise HTTPException(404, "便签不存在")

    await db.delete(existing)
    await db.commit()
    return {"message": "已删除"}
