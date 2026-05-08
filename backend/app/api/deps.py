"""认证依赖注入 - 获取当前登录用户"""
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.security import decode_token
from app.models.family import User

security = HTTPBearer()


async def get_current_user(
    credentials=Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """从 Bearer token 解码并返回当前用户（含 member 关系）"""
    payload = decode_token(credentials.credentials)
    if not payload:
        raise HTTPException(401, "无效的认证令牌")
    result = await db.execute(
        select(User)
        .where(User.id == int(payload["sub"]))
        .options(selectinload(User.member))
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(401, "用户不存在")
    return user
