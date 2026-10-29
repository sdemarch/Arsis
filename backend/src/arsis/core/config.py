import os
import sys
from functools import lru_cache
from pathlib import Path
from typing import Self

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[4]


def default_data_dir() -> Path:
    """Return a writable data directory without coupling packaged data to the app binary."""

    if getattr(sys, "frozen", False):
        local_app_data = os.environ.get("LOCALAPPDATA")
        base = Path(local_app_data) if local_app_data else Path.home() / "AppData" / "Local"
        return base / "Arsis"
    return PROJECT_ROOT / "data"


def application_root() -> Path:
    """Return the directory that contains bundled, read-only application assets."""

    if getattr(sys, "frozen", False):
        return Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent))
    return PROJECT_ROOT


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: str = "local"
    app_secret_key: str = Field(default="local-development-secret-key-change-me", min_length=32)
    arsis_data_dir: Path | None = None
    serve_frontend: bool = False
    frontend_dist_dir: Path | None = None
    local_bind_host: str = "127.0.0.1"
    local_bind_port: int = Field(default=8765, ge=1, le=65535)
    allowed_origins: str = "http://localhost:4200"
    access_token_ttl: int = Field(default=900, ge=60, le=3600)
    refresh_token_ttl: int = Field(default=2_592_000, ge=300, le=31_536_000)
    refresh_cookie_name: str = "arsis_refresh_token"
    log_level: str = "INFO"

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]

    @property
    def data_dir(self) -> Path:
        path = (self.arsis_data_dir or default_data_dir()).expanduser()
        if not path.is_absolute():
            path = PROJECT_ROOT / path
        return path.resolve()

    @property
    def database_path(self) -> Path:
        return self.data_dir / "arsis.db"

    @property
    def attachments_dir(self) -> Path:
        return self.data_dir / "attachments"

    @property
    def backups_dir(self) -> Path:
        return self.data_dir / "backups"

    @property
    def frontend_dir(self) -> Path:
        default_frontend_dir = (
            application_root() / "frontend"
            if getattr(sys, "frozen", False)
            else PROJECT_ROOT / "frontend" / "dist" / "arsis" / "browser"
        )
        path = self.frontend_dist_dir or default_frontend_dir
        path = path.expanduser()
        if not path.is_absolute():
            path = application_root() / path
        return path.resolve()

    @property
    def database_url(self) -> str:
        return f"sqlite:///{self.database_path.as_posix()}"

    @property
    def refresh_cookie_secure(self) -> bool:
        return self.app_env.lower() in {"production", "staging"}

    @model_validator(mode="after")
    def require_production_secret(self) -> Self:
        if self.app_env.lower() in {"production", "staging"} and (
            "change-me" in self.app_secret_key.lower()
            or self.app_secret_key == "replace-with-at-least-32-random-characters"
        ):
            raise ValueError("APP_SECRET_KEY deve essere casuale in staging e produzione")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
