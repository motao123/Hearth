from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.core.config import settings
from app.core.database import init_db

limiter = Limiter(key_func=get_remote_address, default_limits=[])


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title="Hearth",
    description="Self-hosted household hub",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
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

# Serve frontend in production
app.mount("/", StaticFiles(directory="public", html=True), name="frontend")
