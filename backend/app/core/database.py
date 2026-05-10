import logging
import os
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

logger = logging.getLogger("hearth.database")

os.makedirs(os.path.dirname(settings.db_path) or ".", exist_ok=True)

engine = create_async_engine(f"sqlite+aiosqlite:///{settings.db_path}", echo=settings.debug)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_db():
    async with async_session() as session:
        yield session


async def init_db():
    """Initialize database tables. Tries alembic first, falls back to create_all."""
    try:
        from alembic.config import Config
        from alembic import command
        import os.path
        base = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        alembic_cfg = Config(os.path.join(base, "alembic.ini"))
        alembic_cfg.set_main_option("script_location", os.path.join(base, "alembic"))
        command.upgrade(alembic_cfg, "head")
    except (ImportError, FileNotFoundError):
        logger.info("Alembic not available, using create_all fallback")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    except Exception as e:
        logger.warning("Alembic migration failed: %s, falling back to create_all", e)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
