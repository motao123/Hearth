import asyncio
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.core.config import settings
from app.core.database import init_db, async_session

limiter = Limiter(key_func=get_remote_address, default_limits=[])


async def _cleanup_revoked_tokens():
    """Background task: periodically remove expired revoked tokens."""
    from datetime import datetime, timezone
    from sqlalchemy import delete, text
    from app.models.family import RevokedToken
    while True:
        await asyncio.sleep(3600)  # every hour
        try:
            async with async_session() as db:
                await db.execute(
                    delete(RevokedToken).where(
                        RevokedToken.expires_at < datetime.now(timezone.utc)
                    )
                )
                await db.commit()
        except Exception:
            pass


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    task = asyncio.create_task(_cleanup_revoked_tokens())
    yield
    task.cancel()


app = FastAPI(
    title="Hearth",
    description="Self-hosted household hub",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/api/docs" if settings.debug else None,
    openapi_url="/api/openapi.json" if settings.debug else None,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept"],
)


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'; connect-src 'self'; frame-ancestors 'none'"
    if not settings.debug:
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    # Prevent caching of index.html to avoid stale asset references after rebuilds
    if request.url.path in ("/", "/index.html"):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return response


@app.get("/api/health")
async def health():
    return {"status": "ok"}


# API routes
from app.api import auth, tasks, shopping, meals, budget, calendar, notes, family, files  # noqa: E402

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(family.router, prefix="/api/family", tags=["family"])
app.include_router(tasks.router, prefix="/api/tasks", tags=["tasks"])
app.include_router(shopping.router, prefix="/api/shopping", tags=["shopping"])
app.include_router(meals.router, prefix="/api/meals", tags=["meals"])
app.include_router(budget.router, prefix="/api/budget", tags=["budget"])
app.include_router(calendar.router, prefix="/api/calendar", tags=["calendar"])
app.include_router(notes.router, prefix="/api/notes", tags=["notes"])
app.include_router(files.router, prefix="/api/files", tags=["files"])

# Serve frontend in production (only if public/ directory exists)
if os.path.isdir("public"):
    app.mount("/", StaticFiles(directory="public", html=True), name="frontend")
