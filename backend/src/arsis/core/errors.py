from collections.abc import Mapping
from typing import Any


class DomainError(Exception):
    """Base class for errors that are safe to expose through the API."""

    def __init__(
        self,
        *,
        code: str,
        message: str,
        status_code: int,
        details: Mapping[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = dict(details) if details else None


class ResourceNotFoundError(DomainError):
    def __init__(self, resource: str, resource_id: str) -> None:
        super().__init__(
            code="RESOURCE_NOT_FOUND",
            message=f"Risorsa non trovata: {resource}",
            status_code=404,
            details={"resource": resource, "resource_id": resource_id},
        )


class ConflictError(DomainError):
    def __init__(
        self,
        message: str,
        *,
        code: str = "CONFLICT",
        details: Mapping[str, Any] | None = None,
    ) -> None:
        super().__init__(code=code, message=message, status_code=409, details=details)


class StaleVersionError(ConflictError):
    def __init__(self, *, expected_version: int, current_version: int) -> None:
        super().__init__(
            "Il record è stato modificato da un'altra operazione",
            code="STALE_VERSION",
            details={
                "expected_version": expected_version,
                "current_version": current_version,
            },
        )


class InvalidSortError(DomainError):
    def __init__(self, field: str, allowed_fields: set[str]) -> None:
        super().__init__(
            code="INVALID_SORT",
            message=f"Ordinamento non supportato: {field}",
            status_code=422,
            details={"field": field, "allowed_fields": sorted(allowed_fields)},
        )

