from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=("../.env", ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: str = "local"
    app_secret_key: str = Field(default="local-development-only", min_length=16)
    arsis_data_dir: Path = Path("./data")
    allowed_origins: str = "http://localhost:4200"
    log_level: str = "INFO"

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]

    @property
    def data_dir(self) -> Path:
        path = self.arsis_data_dir.expanduser()
        if not path.is_absolute():
            path = Path(__file__).resolve().parents[4] / path
        return path.resolve()

    @property
    def database_path(self) -> Path:
        return self.data_dir / "arsis.db"

    @property
    def database_url(self) -> str:
        return f"sqlite:///{self.database_path.as_posix()}"


@lru_cache
def get_settings() -> Settings:
    return Settings()
