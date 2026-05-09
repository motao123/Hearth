"""认证依赖注入 - 获取当前登录用户"""
from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.security import decode_token
from app.models.family import User, RevokedToken

security = HTTPBearer(auto_error=False)

COOKIE_NAME = "hearth_token"


async def get_current_user(
    request: Request,
    credentials=Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """从 httpOnly cookie 或 Bearer token 解码并返回当前用户"""
    # Try cookie first, then Authorization header
    token = request.cookies.get(COOKIE_NAME)
    if not token and credentials:
        token = credentials.credentials
    if not token:
        raise HTTPException(401, "未提供认证令牌")

    payload = decode_token(token)
    if not payload:
        raise HTTPException(401, "无效的认证令牌")

    # Check if token has been revoked
    jti = payload.get("jti")
    if jti:
        revoked = (await db.execute(
            select(RevokedToken).where(RevokedToken.jti == jti)
        )).scalar_one_or_none()
        if revoked:
            raise HTTPException(401, "令牌已失效")

    result = await db.execute(
        select(User)
        .where(User.id == int(payload["sub"]))
        .options(selectinload(User.member))
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(401, "用户不存在")
    return user


async def require_admin(user: User = Depends(get_current_user)) -> User:
    """要求当前用户为管理员"""
    if not user.is_admin:
        raise HTTPException(403, "需要管理员权限")
    return user
