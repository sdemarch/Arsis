from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from arsis.core.config import get_settings
from arsis.core.database import dispose_database_engine, get_database_engine
from arsis.core.logging import configure_logging
from arsis.health.router import router as health_router

settings = get_settings()
configure_logging(settings.log_level)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    get_database_engine()
    try:
        yield
    finally:
        dispose_database_engine()


app = FastAPI(title="Arsis API", version="0.1.0", docs_url="/docs", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_v1 = APIRouter(prefix="/api/v1")


@api_v1.get("")
def api_index() -> dict[str, str]:
    return {"name": "Arsis API", "version": "v1"}


app.include_router(health_router)
app.include_router(api_v1)

