"""收支预算接口 - 增删改查、月度摘要、红包人情、CSV导出"""
import csv
import io
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field, field_validator
from typing import Literal
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.family import BudgetEntry, User
from app.api.deps import get_current_user
from app.utils.sanitize import strip_html

router = APIRouter()


class EntryCreate(BaseModel):
    type: Literal["income", "expense"]
    amount: float = Field(gt=0)
    category: str = Field(max_length=50)
    description: str | None = Field(default=None, max_length=200)
    date: str = Field(max_length=10)
    member_id: int | None = None
    is_recurring: bool = False
    is_hongbao: bool = False
    counterparty: str | None = Field(default=None, max_length=100)

    @field_validator("category", "description", "counterparty", mode="before")
    @classmethod
    def _sanitize(cls, v):
        return strip_html(v)


class EntryUpdate(BaseModel):
    type: Literal["income", "expense"] | None = None
    amount: float | None = Field(default=None, gt=0)
    category: str | None = Field(default=None, max_length=50)
    description: str | None = Field(default=None, max_length=200)
    date: str | None = Field(default=None, max_length=10)
    member_id: int | None = None
    is_recurring: bool | None = None
    is_hongbao: bool | None = None
    counterparty: str | None = Field(default=None, max_length=100)

    @field_validator("category", "description", "counterparty", mode="before")
    @classmethod
    def _sanitize(cls, v):
        return strip_html(v)


def _entry_dict(e: BudgetEntry) -> dict:
    return {
        "id": e.id,
        "family_id": e.family_id,
        "type": e.type,
        "amount": e.amount,
        "category": e.category,
        "description": e.description,
        "date": e.date,
        "member_id": e.member_id,
        "is_recurring": e.is_recurring,
        "is_hongbao": e.is_hongbao,
        "counterparty": e.counterparty,
        "created_at": e.created_at.isoformat() if e.created_at else None,
    }


@router.get("/entries")
async def list_entries(
    year: int | None = None,
    month: int | None = None,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取某月的收支记录"""
    if not user.member:
        raise HTTPException(403, "当前用户未关联家庭成员")
    family_id = user.member.family_id

    now = datetime.now(timezone.utc)
    year = year or now.year
    month = month or now.month

    # 构建日期范围
    start_date = f"{year:04d}-{month:02d}-01"
    if month == 12:
        end_date = f"{year + 1:04d}-01-01"
    else:
        end_date = f"{year:04d}-{month + 1:02d}-01"

    result = await db.execute(
        select(BudgetEntry).where(
            BudgetEntry.family_id == family_id,
            BudgetEntry.date >= start_date,
            BudgetEntry.date < end_date,
        ).order_by(BudgetEntry.date.desc())
    )
    entries = result.scalars().all()
    return [_entry_dict(e) for e in entries]


@router.post("/entries")
async def add_entry(
    entry: EntryCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """添加收支记录"""
    if not user.member:
        raise HTTPException(403, "当前用户未关联家庭成员")
    family_id = user.member.family_id

    new_entry = BudgetEntry(
        family_id=family_id,
        type=entry.type,
        amount=entry.amount,
        category=entry.category,
        description=entry.description,
        date=entry.date,
        member_id=entry.member_id,
        is_recurring=entry.is_recurring,
        is_hongbao=entry.is_hongbao,
        counterparty=entry.counterparty,
    )
    db.add(new_entry)
    await db.commit()
    await db.refresh(new_entry)
    return _entry_dict(new_entry)


@router.patch("/entries/{entry_id}")
async def update_entry(
    entry_id: int,
    entry: EntryUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """更新收支记录"""
    if not user.member:
        raise HTTPException(403, "当前用户未关联家庭成员")
    family_id = user.member.family_id

    result = await db.execute(
        select(BudgetEntry).where(BudgetEntry.id == entry_id, BudgetEntry.family_id == family_id)
    )
    existing = result.scalar_one_or_none()
    if not existing:
        raise HTTPException(404, "记录不存在")

    update_data = entry.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(existing, field, value)

    await db.commit()
    await db.refresh(existing)
    return _entry_dict(existing)


@router.delete("/entries/{entry_id}")
async def delete_entry(
    entry_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """删除收支记录"""
    if not user.member:
        raise HTTPException(403, "当前用户未关联家庭成员")
    family_id = user.member.family_id

    result = await db.execute(
        select(BudgetEntry).where(BudgetEntry.id == entry_id, BudgetEntry.family_id == family_id)
    )
    existing = result.scalar_one_or_none()
    if not existing:
        raise HTTPException(404, "记录不存在")

    await db.delete(existing)
    await db.commit()
    return {"message": "已删除"}


@router.get("/summary")
async def monthly_summary(
    year: int | None = None,
    month: int | None = None,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """月度消费摘要 - 按类别汇总收支"""
    if not user.member:
        raise HTTPException(403, "当前用户未关联家庭成员")
    family_id = user.member.family_id

    now = datetime.now(timezone.utc)
    year = year or now.year
    month = month or now.month

    start_date = f"{year:04d}-{month:02d}-01"
    if month == 12:
        end_date = f"{year + 1:04d}-01-01"
    else:
        end_date = f"{year:04d}-{month + 1:02d}-01"

    # 按类别汇总收入
    income_result = await db.execute(
        select(BudgetEntry.category, func.sum(BudgetEntry.amount).label("total"))
        .where(
            BudgetEntry.family_id == family_id,
            BudgetEntry.type == "income",
            BudgetEntry.date >= start_date,
            BudgetEntry.date < end_date,
        )
        .group_by(BudgetEntry.category)
    )
    income_by_category = [
        {"category": cat, "total": total} for cat, total in income_result.all()
    ]

    # 按类别汇总支出
    expense_result = await db.execute(
        select(BudgetEntry.category, func.sum(BudgetEntry.amount).label("total"))
        .where(
            BudgetEntry.family_id == family_id,
            BudgetEntry.type == "expense",
            BudgetEntry.date >= start_date,
            BudgetEntry.date < end_date,
        )
        .group_by(BudgetEntry.category)
    )
    expense_by_category = [
        {"category": cat, "total": total} for cat, total in expense_result.all()
    ]

    # 总计
    total_income = sum(item["total"] or 0 for item in income_by_category)
    total_expense = sum(item["total"] or 0 for item in expense_by_category)

    return {
        "year": year,
        "month": month,
        "total_income": total_income,
        "total_expense": total_expense,
        "balance": total_income - total_expense,
        "income_by_category": income_by_category,
        "expense_by_category": expense_by_category,
    }


@router.get("/hongbao")
async def list_hongbao(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """红包/人情往来记录"""
    if not user.member:
        raise HTTPException(403, "当前用户未关联家庭成员")
    family_id = user.member.family_id

    result = await db.execute(
        select(BudgetEntry)
        .where(BudgetEntry.family_id == family_id, BudgetEntry.is_hongbao == True)
        .order_by(BudgetEntry.date.desc())
    )
    entries = result.scalars().all()
    return [_entry_dict(e) for e in entries]


@router.get("/export")
async def export_csv(
    year: int | None = None,
    month: int | None = None,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """导出某月收支记录为 CSV"""
    if not user.member:
        raise HTTPException(403, "当前用户未关联家庭成员")
    family_id = user.member.family_id

    now = datetime.now(timezone.utc)
    year = year or now.year
    month = month or now.month

    start_date = f"{year:04d}-{month:02d}-01"
    if month == 12:
        end_date = f"{year + 1:04d}-01-01"
    else:
        end_date = f"{year:04d}-{month + 1:02d}-01"

    result = await db.execute(
        select(BudgetEntry).where(
            BudgetEntry.family_id == family_id,
            BudgetEntry.date >= start_date,
            BudgetEntry.date < end_date,
        ).order_by(BudgetEntry.date)
    )
    entries = result.scalars().all()

    # 生成 CSV
    output = io.StringIO()
    # 使用 utf-8-sig 以便 Excel 正确识别中文
    writer = csv.writer(output)
    writer.writerow(["日期", "类型", "金额", "分类", "描述", "红包", "对方", "周期性"])
    for e in entries:
        writer.writerow([
            e.date,
            "收入" if e.type == "income" else "支出",
            e.amount,
            e.category,
            e.description or "",
            "是" if e.is_hongbao else "否",
            e.counterparty or "",
            "是" if e.is_recurring else "否",
        ])

    output.seek(0)
    content = output.getvalue().encode("utf-8-sig")
    filename = f"budget_{year:04d}_{month:02d}.csv"

    return StreamingResponse(
        io.BytesIO(content),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
