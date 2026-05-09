"""认证接口 - 注册、登录、获取当前用户"""
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel, Field
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.core.security import create_token, decode_token, hash_password, verify_password
from app.models.family import Family, Member, User, RevokedToken
from app.api.deps import get_current_user

router = APIRouter()
limiter = Limiter(key_func=get_remote_address, default_limits=[])

COOKIE_NAME = "hearth_token"


def _set_token_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key=COOKIE_NAME,
        value=token,
        httponly=True,
        secure=not settings.debug,
        samesite="lax",
        max_age=settings.session_expire_hours * 3600,
        path="/",
    )


def _clear_token_cookie(response: Response) -> None:
    response.set_cookie(
        key=COOKIE_NAME,
        value="",
        httponly=True,
        secure=not settings.debug,
        samesite="lax",
        max_age=0,
        path="/",
    )


class LoginRequest(BaseModel):
    username: str = Field(max_length=50)
    password: str = Field(max_length=128)


class RegisterRequest(BaseModel):
    username: str = Field(min_length=2, max_length=50)
    password: str = Field(min_length=8, max_length=128)
    name: str = Field(min_length=1, max_length=50)

    def model_post_init(self, __context):
        if len(self.password) < 8:
            raise ValueError("密码长度不能少于8位")
        if not any(c.isalpha() for c in self.password) or not any(c.isdigit() for c in self.password):
            raise ValueError("密码必须包含字母和数字")
        if len(self.username) < 2:
            raise ValueError("用户名长度不能少于2位")


class AuthResponse(BaseModel):
    is_admin: bool


class UserInfoResponse(BaseModel):
    id: int
    username: str
    is_admin: bool
    name: str | None = None
    family_id: int | None = None
    member_id: int | None = None


@router.post("/register", response_model=AuthResponse)
@limiter.limit("3/minute")
async def register(request: Request, response: Response, req: RegisterRequest, db: AsyncSession = Depends(get_db)):
    """注册新用户 - 自动创建家庭和成员"""
    exists = (await db.execute(select(User).where(User.username == req.username))).scalar_one_or_none()
    if exists:
        raise HTTPException(400, "用户名已存在")

    # 创建家庭
    family = Family(name=f"{req.name}的家庭")
    db.add(family)
    await db.flush()

    # 创建成员
    member = Member(family_id=family.id, name=req.name, role="admin")
    db.add(member)
    await db.flush()

    # 创建用户并关联成员 — 第一个用户为管理员，后续用户默认非管理员
    user_count = (await db.execute(select(func.count(User.id)))).scalar() or 0
    user = User(
        username=req.username,
        hashed_password=hash_password(req.password),
        is_admin=(user_count == 0),
        member_id=member.id,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    token = create_token(user.id)
    _set_token_cookie(response, token)
    return AuthResponse(is_admin=user.is_admin)


@router.post("/login", response_model=AuthResponse)
@limiter.limit("5/minute")
async def login(request: Request, response: Response, req: LoginRequest, db: AsyncSession = Depends(get_db)):
    """用户登录 - 设置 httpOnly cookie"""
    user = (await db.execute(select(User).where(User.username == req.username))).scalar_one_or_none()

    if not user:
        raise HTTPException(401, "用户名或密码错误")

    # Check account lockout
    if user.locked_until and user.locked_until > datetime.now(timezone.utc):
        remaining = (user.locked_until - datetime.now(timezone.utc)).seconds // 60
        raise HTTPException(403, f"账户已锁定，请{remaining}分钟后重试")

    # Clear expired lockout
    if user.locked_until and user.locked_until <= datetime.now(timezone.utc):
        user.failed_login_attempts = 0
        user.locked_until = None

    if not verify_password(req.password, user.hashed_password):
        # Increment failed attempts
        user.failed_login_attempts = (user.failed_login_attempts or 0) + 1
        if user.failed_login_attempts >= 5:
            user.locked_until = datetime.now(timezone.utc) + timedelta(minutes=15)
        await db.commit()
        raise HTTPException(401, "用户名或密码错误")

    # Reset failed attempts on successful login
    if user.failed_login_attempts > 0:
        user.failed_login_attempts = 0
        user.locked_until = None
        await db.commit()

    token = create_token(user.id)
    _set_token_cookie(response, token)
    return AuthResponse(is_admin=user.is_admin)


@router.post("/logout")
async def logout(
    request: Request,
    response: Response,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """登出 - 将当前令牌加入黑名单并清除 cookie"""
    token = request.cookies.get(COOKIE_NAME)
    if token:
        payload = decode_token(token)
        if payload and payload.get("jti"):
            revoked = RevokedToken(
                jti=payload["jti"],
                expires_at=datetime.fromtimestamp(payload["exp"], tz=timezone.utc),
            )
            db.add(revoked)
            await db.commit()
    _clear_token_cookie(response)
    return {"message": "已登出"}


@router.get("/me", response_model=UserInfoResponse)
async def me(user: User = Depends(get_current_user)):
    """获取当前用户信息"""
    return UserInfoResponse(
        id=user.id,
        username=user.username,
        is_admin=user.is_admin,
        name=user.member.name if user.member else None,
        family_id=user.member.family_id if user.member else None,
        member_id=user.member_id,
    )
