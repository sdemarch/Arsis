"""HTTP endpoints to export and import `.arsis-save` files.

Import replaces every local datum, so it requires the responsible's password
and is refused while other requests are running (see ``arsis.core.maintenance``).
"""

import shutil
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, Response, UploadFile
from fastapi.responses import FileResponse
from starlette.background import BackgroundTask

from arsis.auth.dependencies import CurrentUser
from arsis.auth.router import clear_refresh_cookie
from arsis.core.api_models import ERROR_RESPONSES
from arsis.core.config import Settings, get_settings
from arsis.core.errors import DomainError
from arsis.core.maintenance import maintenance_gate
from arsis.core.security import verify_password
from arsis.maintenance.schemas import SaveImportResult, SaveSummary
from arsis.maintenance.service import SaveService, save_file_name, staging_dir

router = APIRouter(prefix="/api/v1/maintenance", tags=["maintenance"])
_service = SaveService(maintenance_gate)

SaveUpload = Annotated[UploadFile, File(description="File .arsis-save")]


@contextmanager
def _staged(upload: UploadFile, settings: Settings) -> Iterator[Path]:
    path = staging_dir(settings) / f"upload-{uuid4().hex}.arsis-save"
    try:
        with path.open("wb") as stream:
            shutil.copyfileobj(upload.file, stream, 1024 * 1024)
        yield path
    finally:
        path.unlink(missing_ok=True)


@router.get(
    "/saves/export",
    response_class=FileResponse,
    responses={200: {"content": {"application/octet-stream": {}}}, **ERROR_RESPONSES},
)
def export_save(
    _current_user: CurrentUser,
    settings: Annotated[Settings, Depends(get_settings)],
) -> FileResponse:
    path = _service.export(settings)
    return FileResponse(
        path,
        media_type="application/octet-stream",
        filename=save_file_name(datetime.now()),
        background=BackgroundTask(path.unlink, missing_ok=True),
    )


@router.post("/saves/inspect", response_model=SaveSummary, responses=ERROR_RESPONSES)
def inspect_save(
    file: SaveUpload,
    _current_user: CurrentUser,
    settings: Annotated[Settings, Depends(get_settings)],
) -> SaveSummary:
    with _staged(file, settings) as path:
        return _service.describe(path, settings)


@router.post("/saves/import", response_model=SaveImportResult, responses=ERROR_RESPONSES)
def import_save(
    file: SaveUpload,
    password: Annotated[str, Form()],
    current_user: CurrentUser,
    settings: Annotated[Settings, Depends(get_settings)],
    response: Response,
) -> SaveImportResult:
    valid, _ = verify_password(password, current_user.password_hash)
    if not valid:
        raise DomainError(
            code="PASSWORD_MISMATCH", message="La password non è corretta", status_code=422
        )
    with _staged(file, settings) as path:
        result = _service.import_save(path, settings)
    # The refresh session belonged to the replaced data: sign in again.
    clear_refresh_cookie(response, settings)
    return result
