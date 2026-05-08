"""认证接口 - 注册、登录、获取当前用户"""
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import create_token, hash_password, verify_password
from app.models.family import Family, Member, User
from app.api.deps import get_current_user

router = APIRouter()
limiter = Limiter(key_func=get_remote_address, default_limits=[])


class LoginRequest(BaseModel):
    username: str
    password: str


class RegisterRequest(BaseModel):
    username: str
    password: str
    name: str

    def model_post_init(self, __context):
        if len(self.password) < 6:
            raise ValueError("密码长度不能少于6位")
        if len(self.username) < 2:
            raise ValueError("用户名长度不能少于2位")


class TokenResponse(BaseModel):
    token: str
    is_admin: bool


class UserInfoResponse(BaseModel):
    id: int
    username: str
    is_admin: bool
    name: str | None = None
    family_id: int | None = None
    member_id: int | None = None


@router.post("/register", response_model=TokenResponse)
@limiter.limit("3/minute")
async def register(request: Request, req: RegisterRequest, db: AsyncSession = Depends(get_db)):
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

    # 创建用户并关联成员
    user = User(
        username=req.username,
        hashed_password=hash_password(req.password),
        is_admin=True,
        member_id=member.id,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    return TokenResponse(token=create_token(user.id), is_admin=user.is_admin)


@router.post("/login", response_model=TokenResponse)
@limiter.limit("5/minute")
async def login(request: Request, req: LoginRequest, db: AsyncSession = Depends(get_db)):
    """用户登录 - 返回 JWT 令牌"""
    user = (await db.execute(select(User).where(User.username == req.username))).scalar_one_or_none()
    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(401, "用户名或密码错误")
    return TokenResponse(token=create_token(user.id), is_admin=user.is_admin)


@router.post("/logout")
async def logout():
    """登出 - JWT 无服务端状态，客户端删除令牌即可"""
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
