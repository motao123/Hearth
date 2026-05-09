from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Family(Base):
    __tablename__ = "families"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    members: Mapped[list["Member"]] = relationship(back_populates="family")


class Member(Base):
    __tablename__ = "members"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    family_id: Mapped[int] = mapped_column(ForeignKey("families.id"))
    name: Mapped[str] = mapped_column(String(50))
    role: Mapped[str] = mapped_column(String(20), default="member")  # admin / member / child
    avatar: Mapped[str] = mapped_column(String(255), nullable=True)
    phone: Mapped[str] = mapped_column(String(20), nullable=True)
    email: Mapped[str] = mapped_column(String(100), nullable=True)
    birthday: Mapped[str] = mapped_column(String(10), nullable=True)  # ISO date or lunar date
    is_lunar: Mapped[bool] = mapped_column(Boolean, default=False)  # 农历生日

    family: Mapped["Family"] = relationship(back_populates="members")


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    member_id: Mapped[int] = mapped_column(ForeignKey("members.id"), nullable=True)
    username: Mapped[str] = mapped_column(String(50), unique=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    failed_login_attempts: Mapped[int] = mapped_column(Integer, default=0)
    locked_until: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, default=None)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    member: Mapped["Member"] = relationship()


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    family_id: Mapped[int] = mapped_column(ForeignKey("families.id"))
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="todo")  # todo / doing / done
    priority: Mapped[str] = mapped_column(String(10), default="normal")  # low / normal / high
    assignee_id: Mapped[int] = mapped_column(ForeignKey("members.id"), nullable=True)
    due_date: Mapped[str] = mapped_column(String(10), nullable=True)
    points: Mapped[int] = mapped_column(Integer, default=0)  # 家务积分
    is_recurring: Mapped[bool] = mapped_column(Boolean, default=False)
    recurring_rule: Mapped[str] = mapped_column(String(100), nullable=True)  # rrule
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)


class ShoppingItem(Base):
    __tablename__ = "shopping_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    family_id: Mapped[int] = mapped_column(ForeignKey("families.id"))
    name: Mapped[str] = mapped_column(String(100))
    aisle: Mapped[str] = mapped_column(String(50), nullable=True)  # 分类/通道
    quantity: Mapped[str] = mapped_column(String(30), nullable=True)
    checked: Mapped[bool] = mapped_column(Boolean, default=False)
    added_by: Mapped[int] = mapped_column(ForeignKey("members.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))


class MealPlan(Base):
    __tablename__ = "meal_plans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    family_id: Mapped[int] = mapped_column(ForeignKey("families.id"))
    date: Mapped[str] = mapped_column(String(10))  # ISO date
    slot: Mapped[str] = mapped_column(String(20))  # breakfast / lunch / dinner
    recipe_id: Mapped[int] = mapped_column(ForeignKey("recipes.id"), nullable=True)
    custom_meal: Mapped[str] = mapped_column(String(200), nullable=True)
    servings: Mapped[int] = mapped_column(Integer, default=4)


class Recipe(Base):
    __tablename__ = "recipes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    family_id: Mapped[int] = mapped_column(ForeignKey("families.id"))
    name: Mapped[str] = mapped_column(String(200))
    ingredients: Mapped[str] = mapped_column(Text)  # JSON array
    steps: Mapped[str] = mapped_column(Text)  # JSON array
    servings: Mapped[int] = mapped_column(Integer, default=4)
    tags: Mapped[str] = mapped_column(String(200), nullable=True)
    image: Mapped[str] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))


class BudgetEntry(Base):
    __tablename__ = "budget_entries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    family_id: Mapped[int] = mapped_column(ForeignKey("families.id"))
    type: Mapped[str] = mapped_column(String(10))  # income / expense
    amount: Mapped[float] = mapped_column(Float)
    category: Mapped[str] = mapped_column(String(50))
    description: Mapped[str] = mapped_column(String(200), nullable=True)
    date: Mapped[str] = mapped_column(String(10))
    member_id: Mapped[int] = mapped_column(ForeignKey("members.id"), nullable=True)
    is_recurring: Mapped[bool] = mapped_column(Boolean, default=False)
    is_hongbao: Mapped[bool] = mapped_column(Boolean, default=False)  # 红包/人情往来
    counterparty: Mapped[str] = mapped_column(String(100), nullable=True)  # 对方（婚丧嫁娶）
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))


class CalendarEvent(Base):
    __tablename__ = "calendar_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    family_id: Mapped[int] = mapped_column(ForeignKey("families.id"))
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text, nullable=True)
    start_time: Mapped[str] = mapped_column(String(20))
    end_time: Mapped[str] = mapped_column(String(20), nullable=True)
    all_day: Mapped[bool] = mapped_column(Boolean, default=False)
    color: Mapped[str] = mapped_column(String(7), nullable=True)
    member_id: Mapped[int] = mapped_column(ForeignKey("members.id"), nullable=True)
    source: Mapped[str] = mapped_column(String(20), default="local")  # local / caldav / ics
    source_id: Mapped[str] = mapped_column(String(255), nullable=True)


class Note(Base):
    __tablename__ = "notes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    family_id: Mapped[int] = mapped_column(ForeignKey("families.id"))
    title: Mapped[str] = mapped_column(String(200), nullable=True)
    content: Mapped[str] = mapped_column(Text, default="")
    color: Mapped[str] = mapped_column(String(7), default="#FFE066")
    pinned: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))


class Upload(Base):
    __tablename__ = "uploads"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    family_id: Mapped[int] = mapped_column(ForeignKey("families.id"))
    filename: Mapped[str] = mapped_column(String(255))
    original_name: Mapped[str] = mapped_column(String(255))
    mime_type: Mapped[str] = mapped_column(String(100))
    size: Mapped[int] = mapped_column(Integer)  # bytes
    path: Mapped[str] = mapped_column(String(500))
    uploaded_by: Mapped[int] = mapped_column(ForeignKey("members.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))


class RevokedToken(Base):
    __tablename__ = "revoked_tokens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    jti: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
