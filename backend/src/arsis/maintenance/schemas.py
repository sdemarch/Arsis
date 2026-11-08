from datetime import datetime

from arsis.core.api_models import ApiModel


class SaveContents(ApiModel):
    people: int
    activities: int
    courses: int
    accounting_movements: int
    responsible_users: int
    attachments: int


class SaveSummary(ApiModel):
    created_at: datetime
    organization_name: str | None
    contents: SaveContents
    pending_migrations: int


class SaveImportResult(ApiModel):
    summary: SaveSummary
    backup_file: str
    applied_migrations: list[str]
