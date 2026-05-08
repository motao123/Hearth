"""日历接口 - 事件增删改查、中国法定节假日、农历转换"""
from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.family import CalendarEvent, User
from app.api.deps import get_current_user
from app.utils.lunar import solar_to_lunar, get_major_lunar_festivals

router = APIRouter()


class EventCreate(BaseModel):
    title: str
    description: str | None = None
    start_time: str
    end_time: str | None = None
    all_day: bool = False
    color: str | None = None
    member_id: int | None = None
    source: str = "local"
    source_id: str | None = None


class EventUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    start_time: str | None = None
    end_time: str | None = None
    all_day: bool | None = None
    color: str | None = None
    member_id: int | None = None


def _event_dict(e: CalendarEvent) -> dict:
    return {
        "id": e.id,
        "family_id": e.family_id,
        "title": e.title,
        "description": e.description,
        "start_time": e.start_time,
        "end_time": e.end_time,
        "all_day": e.all_day,
        "color": e.color,
        "member_id": e.member_id,
        "source": e.source,
        "source_id": e.source_id,
    }


@router.get("/events")
async def list_events(
    start: str,
    end: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not user.member:
        raise HTTPException(403, "当前用户未关联家庭成员")
    family_id = user.member.family_id

    result = await db.execute(
        select(CalendarEvent).where(
            CalendarEvent.family_id == family_id,
            CalendarEvent.start_time >= start,
            CalendarEvent.start_time <= end,
        ).order_by(CalendarEvent.start_time)
    )
    events = result.scalars().all()
    return [_event_dict(e) for e in events]


@router.post("/events")
async def create_event(
    event: EventCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not user.member:
        raise HTTPException(403, "当前用户未关联家庭成员")
    family_id = user.member.family_id

    new_event = CalendarEvent(
        family_id=family_id,
        title=event.title,
        description=event.description,
        start_time=event.start_time,
        end_time=event.end_time,
        all_day=event.all_day,
        color=event.color,
        member_id=event.member_id,
        source=event.source,
        source_id=event.source_id,
    )
    db.add(new_event)
    await db.commit()
    await db.refresh(new_event)
    return _event_dict(new_event)


@router.patch("/events/{event_id}")
async def update_event(
    event_id: int,
    event: EventUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not user.member:
        raise HTTPException(403, "当前用户未关联家庭成员")
    family_id = user.member.family_id

    result = await db.execute(
        select(CalendarEvent).where(CalendarEvent.id == event_id, CalendarEvent.family_id == family_id)
    )
    existing = result.scalar_one_or_none()
    if not existing:
        raise HTTPException(404, "事件不存在")

    update_data = event.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(existing, field, value)

    await db.commit()
    await db.refresh(existing)
    return _event_dict(existing)


@router.delete("/events/{event_id}")
async def delete_event(
    event_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not user.member:
        raise HTTPException(403, "当前用户未关联家庭成员")
    family_id = user.member.family_id

    result = await db.execute(
        select(CalendarEvent).where(CalendarEvent.id == event_id, CalendarEvent.family_id == family_id)
    )
    existing = result.scalar_one_or_none()
    if not existing:
        raise HTTPException(404, "事件不存在")

    await db.delete(existing)
    await db.commit()
    return {"message": "已删除"}


@router.get("/holidays/cn")
async def chinese_holidays(
    year: int = 2026,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """中国法定节假日 + 农历节日（基于 lunarcalendar 库动态计算）"""
    festivals = get_major_lunar_festivals(year)
    return {
        "lunar_festivals": festivals,
        "year": year,
    }


@router.get("/lunar")
async def lunar_calendar(
    solar_date: str,
    user: User = Depends(get_current_user()),
    db: AsyncSession = Depends(get_db()),
):
    """公历转农历（支持 2024-2030 年）"""
    try:
        parts = [int(x) for x in solar_date.split("-")]
        d = date(*parts)
    except (ValueError, TypeError):
        raise HTTPException(400, "日期格式错误，请使用 YYYY-MM-DD")

    result = solar_to_lunar(d)
    if result is None:
        return {
            "solar_date": solar_date,
            "note": "该日期无法计算农历",
        }
    return result
