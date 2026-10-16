"""Public API models and list-query conventions."""

from collections.abc import Sequence
from enum import StrEnum
from typing import Annotated, Any

from fastapi import Query
from pydantic import BaseModel, ConfigDict, Field

from arsis.core.errors import InvalidSortError


class ApiModel(BaseModel):
    """Base for public DTOs; persistence-generated DTOs remain separate."""

    model_config = ConfigDict(
        extra="forbid",
        from_attributes=True,
        str_strip_whitespace=True,
    )


class ApiInfo(ApiModel):
    name: str
    api_version: str


class ErrorBody(ApiModel):
    code: str
    message: str
    details: Any | None = None
    request_id: str


class ErrorResponse(ApiModel):
    error: ErrorBody


class PageMeta(ApiModel):
    page: int = Field(ge=1)
    page_size: int = Field(ge=1, le=100)
    total_items: int = Field(ge=0)
    total_pages: int = Field(ge=0)


class Page[T](ApiModel):
    items: list[T]
    meta: PageMeta


class PaginationParams:
    def __init__(
        self,
        page: Annotated[int, Query(ge=1, description="Pagina, a partire da 1")] = 1,
        page_size: Annotated[
            int,
            Query(ge=1, le=100, description="Elementi per pagina, massimo 100"),
        ] = 25,
    ) -> None:
        self.page = page
        self.page_size = page_size

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size


def build_page[T](
    items: Sequence[T], *, total_items: int, params: PaginationParams
) -> Page[T]:
    total_pages = (
        (total_items + params.page_size - 1) // params.page_size if total_items else 0
    )
    return Page[T](
        items=list(items),
        meta=PageMeta(
            page=params.page,
            page_size=params.page_size,
            total_items=total_items,
            total_pages=total_pages,
        ),
    )


class SortDirection(StrEnum):
    ASC = "asc"
    DESC = "desc"


class SortSpec(ApiModel):
    field: str
    direction: SortDirection


def parse_sort(
    value: str | None,
    *,
    allowed_fields: set[str],
    default_field: str,
    default_direction: SortDirection = SortDirection.ASC,
) -> SortSpec:
    if default_field not in allowed_fields:
        raise ValueError("default_field deve essere incluso in allowed_fields")
    if not value:
        return SortSpec(field=default_field, direction=default_direction)

    descending = value.startswith("-")
    field = value[1:] if descending else value
    if field not in allowed_fields:
        raise InvalidSortError(field, allowed_fields)
    return SortSpec(
        field=field,
        direction=SortDirection.DESC if descending else SortDirection.ASC,
    )


ERROR_RESPONSES: dict[int | str, dict[str, Any]] = {
    404: {"model": ErrorResponse, "description": "Risorsa non trovata"},
    409: {"model": ErrorResponse, "description": "Conflitto o versione obsoleta"},
    422: {"model": ErrorResponse, "description": "Richiesta non valida"},
}
