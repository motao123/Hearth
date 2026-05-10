"""餐饮计划接口 - 餐计划管理、菜谱增删改查、导出配料到购物清单"""
import json

from fastapi import APIRouter, Body, Depends, HTTPException
from pydantic import BaseModel, Field, field_validator
from typing import Literal
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.family import MealPlan, Recipe, ShoppingItem, User
from app.api.deps import get_current_user
from app.utils.sanitize import strip_html

router = APIRouter()


class MealPlanItem(BaseModel):
    date: str = Field(max_length=10)
    slot: Literal["breakfast", "lunch", "dinner"] | None = None
    meal_type: Literal["breakfast", "lunch", "dinner"] | None = None  # 前端字段名
    recipe_id: int | None = None
    custom_meal: str | None = Field(default=None, max_length=200)
    recipe_name: str | None = None  # 前端可能传
    servings: int = Field(default=4, ge=1)

    @field_validator("custom_meal", mode="before")
    @classmethod
    def _sanitize(cls, v):
        return strip_html(v)

    def model_post_init(self, __context):
        if self.slot is None and self.meal_type is not None:
            self.slot = self.meal_type
        if self.slot is None:
            self.slot = "lunch"  # default


class MealPlanSetRequest(BaseModel):
    items: list[MealPlanItem]


def _normalize_recipe_field(v: list[str] | str | None) -> list[str] | None:
    """Convert newline-separated string to list, or pass through list/None."""
    if v is None:
        return None
    if isinstance(v, str):
        return [line.strip() for line in v.split('\n') if line.strip()]
    return [i.strip() for i in v if i.strip()]


class RecipeCreate(BaseModel):
    name: str = Field(max_length=200)
    ingredients: list[str] | str
    steps: list[str] | str
    servings: int = Field(default=4, ge=1)
    cooking_time: int | None = Field(default=None, ge=0)
    difficulty: str | None = Field(default=None, max_length=20)
    description: str | None = Field(default=None, max_length=2000)
    tags: str | None = Field(default=None, max_length=200)
    image: str | None = Field(default=None, max_length=255)

    @field_validator('ingredients', mode='before')
    @classmethod
    def normalize_ingredients(cls, v):
        return _normalize_recipe_field(v)

    @field_validator('steps', mode='before')
    @classmethod
    def normalize_steps(cls, v):
        return _normalize_recipe_field(v)

    @field_validator("name", "description", "tags", mode="before")
    @classmethod
    def _sanitize(cls, v):
        return strip_html(v)


class RecipeUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=200)
    ingredients: list[str] | str | None = None
    steps: list[str] | str | None = None
    servings: int | None = Field(default=None, ge=1)
    cooking_time: int | None = Field(default=None, ge=0)
    difficulty: str | None = Field(default=None, max_length=20)
    description: str | None = Field(default=None, max_length=2000)
    tags: str | None = Field(default=None, max_length=200)
    image: str | None = Field(default=None, max_length=255)

    @field_validator('ingredients', mode='before')
    @classmethod
    def normalize_ingredients(cls, v):
        return _normalize_recipe_field(v)

    @field_validator('steps', mode='before')
    @classmethod
    def normalize_steps(cls, v):
        return _normalize_recipe_field(v)

    @field_validator("name", "description", "tags", mode="before")
    @classmethod
    def _sanitize(cls, v):
        return strip_html(v)


class ExportRequest(BaseModel):
    start_date: str | None = Field(default=None, max_length=10)
    end_date: str | None = Field(default=None, max_length=10)
    date: str | None = Field(default=None, max_length=10)  # frontend compat

    def model_post_init(self, __context):
        if self.date and not self.start_date:
            self.start_date = self.date
            self.end_date = self.date


def _plan_dict(p: MealPlan, recipe_name: str | None = None) -> dict:
    return {
        "id": p.id,
        "family_id": p.family_id,
        "date": p.date,
        "slot": p.slot,
        "recipe_id": p.recipe_id,
        "recipe_name": recipe_name,
        "custom_meal": p.custom_meal,
        "servings": p.servings,
    }


def _recipe_dict(r: Recipe) -> dict:
    return {
        "id": r.id,
        "family_id": r.family_id,
        "name": r.name,
        "ingredients": json.loads(r.ingredients) if r.ingredients else [],
        "steps": json.loads(r.steps) if r.steps else [],
        "servings": r.servings,
        "cooking_time": r.cooking_time,
        "difficulty": r.difficulty,
        "description": r.description,
        "tags": r.tags,
        "image": r.image,
        "created_at": r.created_at.isoformat() if r.created_at else None,
    }


@router.get("/plan")
async def get_meal_plan(
    start_date: str,
    end_date: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取指定日期范围的餐计划"""
    if not user.member:
        raise HTTPException(403, "当前用户未关联家庭成员")
    family_id = user.member.family_id

    result = await db.execute(
        select(MealPlan, Recipe.name)
        .outerjoin(Recipe, MealPlan.recipe_id == Recipe.id)
        .where(
            MealPlan.family_id == family_id,
            MealPlan.date >= start_date,
            MealPlan.date <= end_date,
        )
        .order_by(MealPlan.date, MealPlan.slot)
    )
    rows = result.all()
    return [_plan_dict(p, recipe_name=name) for p, name in rows]


@router.put("/plan")
@router.post("/plan")
async def set_meal_plan(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    body: dict | list = Body(...),
):
    """设置餐计划 - 支持前端直接传单条或 {items: [...]} 或列表"""
    if not user.member:
        raise HTTPException(403, "当前用户未关联家庭成员")
    family_id = user.member.family_id

    # 解析多种输入格式
    raw = body if isinstance(body, list) else body.get("items", [body]) if isinstance(body, dict) else []
    items = [MealPlanItem(**item) for item in raw]

    # 收集所有涉及的日期
    dates = list({item.date for item in items})

    # 删除该日期范围内同日期同餐次的旧记录
    for date in dates:
        slots = [item.slot for item in items if item.date == date]
        for slot in slots:
            await db.execute(
                delete(MealPlan).where(
                    MealPlan.family_id == family_id,
                    MealPlan.date == date,
                    MealPlan.slot == slot,
                )
            )

    # 创建新记录（跳过空计划，即 recipe_id 和 custom_meal 均为空的清除请求）
    created = []
    for item in items:
        if item.recipe_id is None and not item.custom_meal:
            continue
        plan = MealPlan(
            family_id=family_id,
            date=item.date,
            slot=item.slot,
            recipe_id=item.recipe_id,
            custom_meal=item.custom_meal,
            servings=item.servings,
        )
        db.add(plan)
        created.append(item.model_dump())

    await db.commit()
    return {"message": "餐计划已更新", "items": created}


@router.get("/recipes")
async def list_recipes(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取菜谱列表"""
    if not user.member:
        raise HTTPException(403, "当前用户未关联家庭成员")
    family_id = user.member.family_id

    result = await db.execute(
        select(Recipe).where(Recipe.family_id == family_id).order_by(Recipe.created_at.desc())
    )
    recipes = result.scalars().all()
    return [_recipe_dict(r) for r in recipes]


@router.post("/recipes")
async def create_recipe(
    recipe: RecipeCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """创建菜谱"""
    if not user.member:
        raise HTTPException(403, "当前用户未关联家庭成员")
    family_id = user.member.family_id

    new_recipe = Recipe(
        family_id=family_id,
        name=recipe.name,
        ingredients=json.dumps(recipe.ingredients, ensure_ascii=False),
        steps=json.dumps(recipe.steps, ensure_ascii=False),
        servings=recipe.servings,
        cooking_time=recipe.cooking_time,
        difficulty=recipe.difficulty,
        description=recipe.description,
        tags=recipe.tags,
        image=recipe.image,
    )
    db.add(new_recipe)
    await db.commit()
    await db.refresh(new_recipe)
    return _recipe_dict(new_recipe)


@router.get("/recipes/{recipe_id}")
async def get_recipe(
    recipe_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取单个菜谱详情"""
    if not user.member:
        raise HTTPException(403, "当前用户未关联家庭成员")
    family_id = user.member.family_id

    result = await db.execute(
        select(Recipe).where(Recipe.id == recipe_id, Recipe.family_id == family_id)
    )
    recipe = result.scalar_one_or_none()
    if not recipe:
        raise HTTPException(404, "菜谱不存在")
    return _recipe_dict(recipe)


@router.patch("/recipes/{recipe_id}")
async def update_recipe(
    recipe_id: int,
    recipe: RecipeUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """更新菜谱"""
    if not user.member:
        raise HTTPException(403, "当前用户未关联家庭成员")
    family_id = user.member.family_id

    result = await db.execute(
        select(Recipe).where(Recipe.id == recipe_id, Recipe.family_id == family_id)
    )
    existing = result.scalar_one_or_none()
    if not existing:
        raise HTTPException(404, "菜谱不存在")

    update_data = recipe.model_dump(exclude_unset=True)
    # 将列表字段转为 JSON 字符串存储
    if "ingredients" in update_data and update_data["ingredients"] is not None:
        update_data["ingredients"] = json.dumps(update_data["ingredients"], ensure_ascii=False)
    if "steps" in update_data and update_data["steps"] is not None:
        update_data["steps"] = json.dumps(update_data["steps"], ensure_ascii=False)

    for field, value in update_data.items():
        setattr(existing, field, value)

    await db.commit()
    await db.refresh(existing)
    return _recipe_dict(existing)


@router.delete("/recipes/{recipe_id}")
async def delete_recipe(
    recipe_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """删除菜谱"""
    if not user.member:
        raise HTTPException(403, "当前用户未关联家庭成员")
    family_id = user.member.family_id

    result = await db.execute(
        select(Recipe).where(Recipe.id == recipe_id, Recipe.family_id == family_id)
    )
    existing = result.scalar_one_or_none()
    if not existing:
        raise HTTPException(404, "菜谱不存在")

    await db.delete(existing)
    await db.commit()
    return {"message": "已删除"}


@router.post("/export-to-shopping")
async def export_to_shopping(
    req: ExportRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """将餐计划中的配料导出到购物清单"""
    if not user.member:
        raise HTTPException(403, "当前用户未关联家庭成员")
    family_id = user.member.family_id

    # 获取日期范围内的餐计划
    plan_result = await db.execute(
        select(MealPlan).where(
            MealPlan.family_id == family_id,
            MealPlan.date >= req.start_date,
            MealPlan.date <= req.end_date,
        )
    )
    plans = plan_result.scalars().all()

    # 收集所有关联的菜谱ID
    recipe_ids = [p.recipe_id for p in plans if p.recipe_id is not None]
    if not recipe_ids:
        return {"message": "餐计划中没有关联菜谱", "added": 0}

    # 获取菜谱
    recipes_result = await db.execute(
        select(Recipe).where(Recipe.id.in_(recipe_ids))
    )
    recipes = recipes_result.scalars().all()
    recipe_map = {r.id: r for r in recipes}

    # 获取已有购物项
    existing_result = await db.execute(
        select(ShoppingItem.name).where(ShoppingItem.family_id == family_id)
    )
    existing_names = {name.lower() for (name,) in existing_result.all()}

    # 提取所有配料并添加到购物清单
    added = 0
    for plan in plans:
        if plan.recipe_id and plan.recipe_id in recipe_map:
            recipe = recipe_map[plan.recipe_id]
            ingredients = json.loads(recipe.ingredients) if recipe.ingredients else []
            for ingredient in ingredients:
                ingredient_name = ingredient.strip()
                if ingredient_name and ingredient_name.lower() not in existing_names:
                    new_item = ShoppingItem(
                        family_id=family_id,
                        name=ingredient_name,
                        added_by=user.member_id,
                    )
                    db.add(new_item)
                    existing_names.add(ingredient_name.lower())
                    added += 1

    await db.commit()
    return {"message": f"已导出 {added} 项配料到购物清单", "added": added}
