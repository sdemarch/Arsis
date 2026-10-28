from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import APIRouter, Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRoute

from arsis.activities.router import router as activities_router
from arsis.auth.dependencies import get_current_user
from arsis.auth.router import router as auth_router
from arsis.core.api_models import ApiInfo
from arsis.core.config import get_settings
from arsis.core.database import dispose_database_engine, get_database_engine
from arsis.core.exception_handlers import install_exception_handlers
from arsis.core.logging import configure_logging
from arsis.core.request_context import RequestIdMiddleware
from arsis.health.router import router as health_router
from arsis.people.router import router as people_router
from arsis.school.router import router as school_router

settings = get_settings()
configure_logging(settings.log_level)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    get_database_engine()
    try:
        yield
    finally:
        dispose_database_engine()


api_v1 = APIRouter(prefix="/api/v1")


@api_v1.get(
    "",
    response_model=ApiInfo,
    tags=["core"],
    dependencies=[Depends(get_current_user)],
)
def api_index() -> ApiInfo:
    return ApiInfo(name="Arsis API", api_version="v1")


def operation_id(route: APIRoute) -> str:
    tag = route.tags[0] if route.tags else "core"
    return f"{tag}_{route.name}"


def create_app() -> FastAPI:
    application = FastAPI(
        title="Arsis API",
        version="0.1.0",
        docs_url="/docs",
        lifespan=lifespan,
        generate_unique_id_function=operation_id,
    )
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID"],
    )
    application.add_middleware(RequestIdMiddleware)
    install_exception_handlers(application)
    application.include_router(health_router)
    application.include_router(auth_router)
    application.include_router(activities_router)
    application.include_router(people_router)
    application.include_router(school_router)
    application.include_router(api_v1)
    return application


app = create_app()
