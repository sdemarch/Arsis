"""Canonical timestamps used by persistence and API services."""

from datetime import UTC, datetime


def utc_now() -> datetime:
    return datetime.now(UTC)


def to_iso8601(value: datetime) -> str:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("Il timestamp deve includere il fuso orario")
    return value.astimezone(UTC).isoformat().replace("+00:00", "Z")


def utc_now_iso() -> str:
    return to_iso8601(utc_now())
