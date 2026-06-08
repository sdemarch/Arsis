from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    DATABASE_URL: str = "mysql+asyncmy://user:password@localhost:3306/arsis"
    SECRET_KEY: str = "dev-secret-change-in-production"
    ENVIRONMENT: str = "development"
    CORS_ORIGINS: List[str] = ["http://localhost:5173"]
    # JWT_SECRET: str = ""  # attivare quando si implementa auth

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
