"""家庭接口 - 成员管理、个人资料、积分排行"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.family import Member, Task, User
from app.api.deps import get_current_user, require_admin

router = APIRouter()


class MemberCreate(BaseModel):
    name: str = Field(max_length=50)
    role: str = Field(default="parent", max_length=20)
    avatar: str | None = Field(default=None, max_length=255)
    phone: str | None = Field(default=None, max_length=20)
    email: str | None = Field(default=None, max_length=100)
    birthday: str | None = Field(default=None, max_length=10)
    is_lunar: bool = False


class MemberUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=50)
    role: str | None = Field(default=None, max_length=20)
    avatar: str | None = Field(default=None, max_length=255)
    phone: str | None = Field(default=None, max_length=20)
    email: str | None = Field(default=None, max_length=100)
    birthday: str | None = Field(default=None, max_length=10)
    is_lunar: bool | None = None


def _member_dict(m: Member) -> dict:
    return {
        "id": m.id,
        "family_id": m.family_id,
        "name": m.name,
        "role": m.role,
        "avatar": m.avatar,
        "phone": m.phone,
        "email": m.email,
        "birthday": m.birthday,
        "is_lunar": m.is_lunar,
    }


@router.get("/members")
async def list_members(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取家庭成员列表"""
    if not user.member:
        raise HTTPException(403, "当前用户未关联家庭成员")
    family_id = user.member.family_id

    result = await db.execute(
        select(Member).where(Member.family_id == family_id).order_by(Member.id)
    )
    members = result.scalars().all()
    return [_member_dict(m) for m in members]


@router.post("/members")
async def add_member(
    create: MemberCreate,
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """添加家庭成员"""
    if not user.member:
        raise HTTPException(403, "当前用户未关联家庭成员")
    family_id = user.member.family_id

    member = Member(
        family_id=family_id,
        name=create.name,
        role=create.role,
        avatar=create.avatar,
        phone=create.phone,
        email=create.email,
        birthday=create.birthday,
        is_lunar=create.is_lunar,
    )
    db.add(member)
    await db.commit()
    await db.refresh(member)
    return _member_dict(member)


@router.get("/members/{member_id}")
async def get_member(
    member_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取单个成员信息"""
    if not user.member:
        raise HTTPException(403, "当前用户未关联家庭成员")
    family_id = user.member.family_id

    result = await db.execute(
        select(Member).where(Member.id == member_id, Member.family_id == family_id)
    )
    member = result.scalar_one_or_none()
    if not member:
        raise HTTPException(404, "成员不存在")
    return _member_dict(member)


@router.patch("/members/{member_id}")
async def update_member(
    member_id: int,
    update: MemberUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """更新成员资料"""
    if not user.member:
        raise HTTPException(403, "当前用户未关联家庭成员")
    family_id = user.member.family_id

    result = await db.execute(
        select(Member).where(Member.id == member_id, Member.family_id == family_id)
    )
    member = result.scalar_one_or_none()
    if not member:
        raise HTTPException(404, "成员不存在")

    update_data = update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(member, field, value)

    await db.commit()
    await db.refresh(member)
    return _member_dict(member)


@router.delete("/members/{member_id}")
async def delete_member(
    member_id: int,
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """删除家庭成员"""
    if not user.member:
        raise HTTPException(403, "当前用户未关联家庭成员")
    family_id = user.member.family_id

    result = await db.execute(
        select(Member).where(Member.id == member_id, Member.family_id == family_id)
    )
    member = result.scalar_one_or_none()
    if not member:
        raise HTTPException(404, "成员不存在")

    # 不允许删除自己
    if member.id == user.member.id:
        raise HTTPException(400, "不能删除自己的成员信息")

    await db.delete(member)
    await db.commit()
    return {"message": "已删除"}


@router.get("/points")
async def get_points_ranking(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """家务积分排行榜 - 统计每个成员已完成任务的积分总和"""
    if not user.member:
        raise HTTPException(403, "当前用户未关联家庭成员")
    family_id = user.member.family_id

    # 查询已完成任务按 assignee_id 汇总积分
    result = await db.execute(
        select(
            Task.assignee_id,
            func.sum(Task.points).label("total_points"),
            func.count(Task.id).label("completed_count"),
        )
        .where(
            Task.family_id == family_id,
            Task.status == "done",
            Task.assignee_id.isnot(None),
        )
        .group_by(Task.assignee_id)
        .order_by(func.sum(Task.points).desc())
    )
    rows = result.all()

    # 获取所有家庭成员信息
    members_result = await db.execute(
        select(Member).where(Member.family_id == family_id)
    )
    members = members_result.scalars().all()
    member_map = {m.id: m for m in members}

    ranking = []
    for assignee_id, total_points, completed_count in rows:
        member = member_map.get(assignee_id)
        if member:
            ranking.append({
                "member_id": assignee_id,
                "name": member.name,
                "avatar": member.avatar,
                "total_points": total_points or 0,
                "completed_count": completed_count or 0,
            })

    # 添加没有完成任何任务的成员
    ranked_ids = {r["member_id"] for r in ranking}
    for m in members:
        if m.id not in ranked_ids:
            ranking.append({
                "member_id": m.id,
                "name": m.name,
                "avatar": m.avatar,
                "total_points": 0,
                "completed_count": 0,
            })

    return ranking
