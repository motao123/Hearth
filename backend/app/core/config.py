from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Server
    host: str = "0.0.0.0"
    port: int = 8090
    debug: bool = False

    # Security
    secret_key: str = ""
    session_expire_hours: int = 72

    @field_validator("secret_key")
    @classmethod
    def _validate_secret_key(cls, v: str) -> str:
        if not v or v.startswith("change-me"):
            raise ValueError(
                "HEARTH_SECRET_KEY must be set to a secure random string. "
                "Generate one with: python -c \"import secrets; print(secrets.token_urlsafe(32))\""
            )
        if len(v) < 32:
            raise ValueError("HEARTH_SECRET_KEY must be at least 32 characters long")
        return v

    # CORS - 逗号分隔的允许域名，生产环境必须设置
    cors_origins: str = "http://localhost:3000,http://localhost:8090"

    # Database
    db_path: str = "data/hearth.db"

    # Backup
    backup_dir: str = "backups"
    backup_cron: str = "0 3 * * *"
    backup_retention: int = 7

    # WeChat Bot (optional)
    wechat_bot_key: str = ""
    wechat_bot_enabled: bool = False

    # Upload
    upload_dir: str = "data/uploads"
    upload_max_size_mb: int = 10

    # Rate Limit
    rate_limit_enabled: bool = True
    rate_limit_login: str = "5/minute"
    rate_limit_register: str = "3/minute"

    model_config = {"env_file": ".env", "env_prefix": "HEARTH_"}

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


settings = Settings()
