"""购物清单接口 - 增删改查、勾选、清空已购、导入配料"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.family import ShoppingItem, User
from app.api.deps import get_current_user

router = APIRouter()


class ItemCreate(BaseModel):
    name: str = Field(max_length=100)
    aisle: str | None = Field(default=None, max_length=50)
    quantity: str | None = Field(default=None, max_length=30)


class ItemUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=100)
    aisle: str | None = Field(default=None, max_length=50)
    quantity: str | None = Field(default=None, max_length=30)
    checked: bool | None = None


class ImportRequest(BaseModel):
    items: list[str] | None = None
    ingredients: list[str] | None = None  # 前端字段名

    def model_post_init(self, __context):
        if self.items is None and self.ingredients is not None:
            self.items = self.ingredients
        if self.items is None:
            self.items = []


def _item_dict(item: ShoppingItem) -> dict:
    return {
        "id": item.id,
        "family_id": item.family_id,
        "name": item.name,
        "aisle": item.aisle,
        "quantity": item.quantity,
        "checked": item.checked,
        "added_by": item.added_by,
        "created_at": item.created_at.isoformat() if item.created_at else None,
    }


@router.get("")
async def list_items(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取购物清单"""
    if not user.member:
        raise HTTPException(403, "当前用户未关联家庭成员")
    family_id = user.member.family_id

    result = await db.execute(
        select(ShoppingItem)
        .where(ShoppingItem.family_id == family_id)
        .order_by(ShoppingItem.checked.asc(), ShoppingItem.created_at.desc())
    )
    items = result.scalars().all()
    return [_item_dict(i) for i in items]


@router.post("")
async def add_item(
    item: ItemCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """添加购物项"""
    if not user.member:
        raise HTTPException(403, "当前用户未关联家庭成员")
    family_id = user.member.family_id

    new_item = ShoppingItem(
        family_id=family_id,
        name=item.name,
        aisle=item.aisle,
        quantity=item.quantity,
        added_by=user.member_id,
    )
    db.add(new_item)
    await db.commit()
    await db.refresh(new_item)
    return _item_dict(new_item)


@router.patch("/{item_id}")
async def update_item(
    item_id: int,
    item: ItemUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """更新购物项 - 可切换勾选状态"""
    if not user.member:
        raise HTTPException(403, "当前用户未关联家庭成员")
    family_id = user.member.family_id

    result = await db.execute(
        select(ShoppingItem).where(ShoppingItem.id == item_id, ShoppingItem.family_id == family_id)
    )
    existing = result.scalar_one_or_none()
    if not existing:
        raise HTTPException(404, "购物项不存在")

    update_data = item.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(existing, field, value)

    await db.commit()
    await db.refresh(existing)
    return _item_dict(existing)


@router.delete("/{item_id}")
async def delete_item(
    item_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """删除购物项"""
    if not user.member:
        raise HTTPException(403, "当前用户未关联家庭成员")
    family_id = user.member.family_id

    result = await db.execute(
        select(ShoppingItem).where(ShoppingItem.id == item_id, ShoppingItem.family_id == family_id)
    )
    existing = result.scalar_one_or_none()
    if not existing:
        raise HTTPException(404, "购物项不存在")

    await db.delete(existing)
    await db.commit()
    return {"message": "已删除"}


@router.post("/clear-checked")
async def clear_checked(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """清空所有已勾选的购物项"""
    if not user.member:
        raise HTTPException(403, "当前用户未关联家庭成员")
    family_id = user.member.family_id

    result = await db.execute(
        select(ShoppingItem).where(ShoppingItem.family_id == family_id, ShoppingItem.checked == True)
    )
    checked_items = result.scalars().all()
    for item in checked_items:
        await db.delete(item)
    await db.commit()
    return {"message": f"已清除 {len(checked_items)} 项"}


@router.post("/import")
async def import_items(
    req: ImportRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """从餐计划导入配料到购物清单"""
    if not user.member:
        raise HTTPException(403, "当前用户未关联家庭成员")
    family_id = user.member.family_id

    # 先获取当前购物清单中已有项的名称，避免重复
    existing_result = await db.execute(
        select(ShoppingItem.name).where(ShoppingItem.family_id == family_id)
    )
    existing_names = {name.lower() for (name,) in existing_result.all()}

    added = 0
    for name in req.items:
        if name.strip().lower() not in existing_names:
            new_item = ShoppingItem(
                family_id=family_id,
                name=name.strip(),
                added_by=user.member_id,
            )
            db.add(new_item)
            existing_names.add(name.strip().lower())
            added += 1

    await db.commit()
    return {"message": f"已导入 {added} 项配料"}
