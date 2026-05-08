"""家务任务接口 - 增删改查、状态更新、积分追踪"""
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.family import Task, User
from app.api.deps import get_current_user

router = APIRouter()


class TaskCreate(BaseModel):
    title: str
    description: str | None = None
    priority: str = "normal"
    assignee_id: int | None = None
    due_date: str | None = None
    points: int = 0
    is_recurring: bool = False
    recurring_rule: str | None = None


class TaskUpdate(BaseModel):
    title: str | None = None
    status: str | None = None
    priority: str | None = None
    assignee_id: int | None = None
    due_date: str | None = None
    points: int | None = None


def _task_dict(t: Task) -> dict:
    return {
        "id": t.id,
        "family_id": t.family_id,
        "title": t.title,
        "description": t.description,
        "status": t.status,
        "priority": t.priority,
        "assignee_id": t.assignee_id,
        "due_date": t.due_date,
        "points": t.points,
        "is_recurring": t.is_recurring,
        "recurring_rule": t.recurring_rule,
        "created_at": t.created_at.isoformat() if t.created_at else None,
        "completed_at": t.completed_at.isoformat() if t.completed_at else None,
    }


@router.get("/")
async def list_tasks(
    status: str | None = None,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取任务列表，可按状态筛选"""
    if not user.member:
        raise HTTPException(403, "当前用户未关联家庭成员")
    family_id = user.member.family_id

    stmt = select(Task).where(Task.family_id == family_id)
    if status:
        stmt = stmt.where(Task.status == status)
    stmt = stmt.order_by(Task.created_at.desc())

    result = await db.execute(stmt)
    tasks = result.scalars().all()
    return [_task_dict(t) for t in tasks]


@router.post("/")
async def create_task(
    task: TaskCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """创建新任务"""
    if not user.member:
        raise HTTPException(403, "当前用户未关联家庭成员")
    family_id = user.member.family_id

    new_task = Task(
        family_id=family_id,
        title=task.title,
        description=task.description,
        priority=task.priority,
        assignee_id=task.assignee_id,
        due_date=task.due_date,
        points=task.points,
        is_recurring=task.is_recurring,
        recurring_rule=task.recurring_rule,
    )
    db.add(new_task)
    await db.commit()
    await db.refresh(new_task)
    return _task_dict(new_task)


@router.patch("/{task_id}")
async def update_task(
    task_id: int,
    task: TaskUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """更新任务 - 完成时自动记录时间并累加积分"""
    if not user.member:
        raise HTTPException(403, "当前用户未关联家庭成员")
    family_id = user.member.family_id

    result = await db.execute(
        select(Task).where(Task.id == task_id, Task.family_id == family_id)
    )
    existing = result.scalar_one_or_none()
    if not existing:
        raise HTTPException(404, "任务不存在")

    # 如果状态变更为 done，记录完成时间
    if task.status == "done" and existing.status != "done":
        existing.completed_at = datetime.utcnow()

    # 如果状态从 done 改回其他状态，清除完成时间
    if task.status and task.status != "done" and existing.status == "done":
        existing.completed_at = None

    update_data = task.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(existing, field, value)

    await db.commit()
    await db.refresh(existing)
    return _task_dict(existing)


@router.delete("/{task_id}")
async def delete_task(
    task_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """删除任务"""
    if not user.member:
        raise HTTPException(403, "当前用户未关联家庭成员")
    family_id = user.member.family_id

    result = await db.execute(
        select(Task).where(Task.id == task_id, Task.family_id == family_id)
    )
    existing = result.scalar_one_or_none()
    if not existing:
        raise HTTPException(404, "任务不存在")

    await db.delete(existing)
    await db.commit()
    return {"message": "已删除"}
