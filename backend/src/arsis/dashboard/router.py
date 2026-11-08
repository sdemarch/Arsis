"""HTTP endpoint for the home dashboard."""

from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from arsis.auth.dependencies import CurrentUser
from arsis.core.api_models import ERROR_RESPONSES
from arsis.core.database import get_database_session
from arsis.dashboard.schemas import DashboardSummary
from arsis.dashboard.service import DashboardService

router = APIRouter(prefix="/api/v1/dashboard", tags=["dashboard"])
_service = DashboardService()


@router.get("/summary", response_model=DashboardSummary, responses=ERROR_RESPONSES)
def get_summary(
    session: Annotated[Session, Depends(get_database_session)],
    _current_user: CurrentUser,
    on: Annotated[date | None, Query(description="Giorno di riferimento, oggi se omesso")] = None,
) -> DashboardSummary:
    # The installation runs on the association's own PC, so its local date is "today".
    return DashboardSummary.model_validate(_service.summary(session, today=on or date.today()))
