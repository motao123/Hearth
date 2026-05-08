"""文件上传接口 - 文档、头像上传"""
import os
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile as FastAPIUploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.models.family import User, Upload
from app.api.deps import get_current_user

router = APIRouter()

ALLOWED_MIME_TYPES = {
    "image/jpeg", "image/png", "image/gif", "image/webp", "image/svg+xml",
    "application/pdf",
    "application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.ms-excel", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "text/plain", "text/csv", "text/markdown",
}

ALLOWED_EXTENSIONS = {
    ".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg",
    ".pdf", ".doc", ".docx", ".xls", ".xlsx",
    ".txt", ".csv", ".md",
}


def _safe_filename(original: str) -> str:
    stem, ext = os.path.splitext(original)
    ext_lower = ext.lower()
    return f"{uuid.uuid4().hex}{ext_lower}"


def _get_upload_dir(family_id: int) -> Path:
    p = Path(settings.upload_dir) / str(family_id)
    p.mkdir(parents=True, exist_ok=True)
    return p


def _upload_dict(u: Upload) -> dict:
    return {
        "id": u.id,
        "family_id": u.family_id,
        "filename": u.filename,
        "original_name": u.original_name,
        "mime_type": u.mime_type,
        "size": u.size,
        "path": u.path,
        "uploaded_by": u.uploaded_by,
        "created_at": u.created_at.isoformat() if u.created_at else None,
    }


@router.get("/")
async def list_uploads(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取所有已上传文件"""
    if not user.member:
        raise HTTPException(403, "当前用户未关联家庭成员")
    family_id = user.member.family_id

    result = await db.execute(
        select(Upload).where(Upload.family_id == family_id).order_by(Upload.created_at.desc())
    )
    uploads = result.scalars().all()
    return [_upload_dict(u) for u in uploads]


@router.post("/")
async def upload_file(
    file: FastAPIUploadFile,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """上传文件（文档/头像）"""
    if not user.member:
        raise HTTPException(403, "当前用户未关联家庭成员")
    family_id = user.member.family_id

    ext = os.path.splitext(file.filename or "unknown")[1].lower()
    if ext not in ALLOWED_EXTENSIONS and file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(400, f"不支持的文件类型: {ext or file.content_type}")

    max_bytes = settings.upload_max_size_mb * 1024 * 1024
    contents = await file.read()
    if len(contents) > max_bytes:
        raise HTTPException(400, f"文件大小不能超过 {settings.upload_max_size_mb}MB")

    safe_name = _safe_filename(file.filename or "unknown")
    upload_dir = _get_upload_dir(family_id)
    file_path = upload_dir / safe_name
    file_path.write_bytes(contents)

    upload = Upload(
        family_id=family_id,
        filename=safe_name,
        original_name=file.filename or "unknown",
        mime_type=file.content_type or "application/octet-stream",
        size=len(contents),
        path=str(file_path),
        uploaded_by=user.member.id,
    )
    db.add(upload)
    await db.commit()
    await db.refresh(upload)
    return _upload_dict(upload)


@router.delete("/{upload_id}")
async def delete_upload(
    upload_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """删除上传文件"""
    if not user.member:
        raise HTTPException(403, "当前用户未关联家庭成员")
    family_id = user.member.family_id

    result = await db.execute(
        select(Upload).where(Upload.id == upload_id, Upload.family_id == family_id)
    )
    upload = result.scalar_one_or_none()
    if not upload:
        raise HTTPException(404, "文件不存在")

    # Delete physical file
    try:
        os.remove(upload.path)
    except OSError:
        pass

    await db.delete(upload)
    await db.commit()
    return {"message": "已删除"}
