"""Audit events recorded inside the caller's domain transaction."""

import json
from collections.abc import Mapping
from typing import Any
from uuid import uuid4

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from arsis.core.request_context import current_request_id
from arsis.core.time import utc_now_iso
from arsis.generated.models import AuditEvent


def record_audit_event(
    session: Session,
    *,
    action: str,
    entity_type: str,
    entity_id: str | None = None,
    user_id: str | None = None,
    details: Mapping[str, Any] | None = None,
    ip_address: str | None = None,
    request_id: str | None = None,
) -> AuditEvent:
    if not action.strip() or not entity_type.strip():
        raise ValueError("action ed entity_type sono obbligatori")

    event = AuditEvent(
        id=str(uuid4()),
        occurred_at=utc_now_iso(),
        user_id=user_id,
        action=action.strip(),
        entity_type=entity_type.strip(),
        entity_id=entity_id,
        request_id=request_id or current_request_id(),
        details=json.dumps(jsonable_encoder(details or {}), ensure_ascii=False, sort_keys=True),
        ip_address=ip_address,
    )
    session.add(event)
    return event
