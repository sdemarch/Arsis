from fastapi import APIRouter, HTTPException, status

from arsis.core.database import create_database_engine, database_is_ready

router = APIRouter(tags=["health"])


@router.get("/health/live")
def live() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/health/ready")
def ready() -> dict[str, str]:
    if not database_is_ready(create_database_engine()):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"code": "DATABASE_UNAVAILABLE", "message": "Database non disponibile"},
        )
    return {"status": "ready"}

