from decimal import Decimal
from typing import Annotated, Literal

from pydantic import Field, PlainSerializer

from arsis.core.api_models import ApiModel

Direction = Literal["income", "expense", "both"]
MovementDirection = Literal["income", "expense"]
Account = Literal["bank", "cash"]
PersonRole = Literal["student", "teacher", "member"]
# SQLite hands NUMERIC values back with ten decimal places: answer with cents.
Money = Annotated[
    Decimal, PlainSerializer(lambda value: str(value.quantize(Decimal("0.01"))), return_type=str)
]


class CategoryCreateRequest(ApiModel):
    name: str = Field(min_length=1, max_length=120)
    direction: Direction
    required_person_role: PersonRole | None = None
    course_required: bool = False
    color: str | None = Field(default=None, pattern=r"^#[0-9A-Fa-f]{6}$")
    display_order: int = Field(default=0, ge=0)


class CategoryUpdateRequest(ApiModel):
    version: int = Field(ge=1)
    name: str | None = Field(default=None, min_length=1, max_length=120)
    direction: Direction | None = None
    required_person_role: PersonRole | None = None
    course_required: bool | None = None
    color: str | None = Field(default=None, pattern=r"^#[0-9A-Fa-f]{6}$")
    is_active: bool | None = None
    display_order: int | None = Field(default=None, ge=0)


class CategoryResponse(CategoryCreateRequest):
    id: int
    is_active: bool
    created_at: str
    updated_at: str
    archived_at: str | None
    version: int


class MovementCreateRequest(ApiModel):
    occurred_on: str = Field(min_length=10, max_length=10)
    direction: MovementDirection
    account: Account
    category_id: int = Field(ge=1)
    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    subject: str = Field(min_length=1, max_length=200)
    person_id: int | None = Field(default=None, ge=1)
    course_id: int | None = Field(default=None, ge=1)
    description: str = Field(min_length=1, max_length=500)
    document_reference: str | None = Field(default=None, max_length=200)


class MovementUpdateRequest(ApiModel):
    version: int = Field(ge=1)
    occurred_on: str | None = Field(default=None, min_length=10, max_length=10)
    direction: MovementDirection | None = None
    account: Account | None = None
    category_id: int | None = Field(default=None, ge=1)
    amount: Decimal | None = Field(default=None, gt=0, max_digits=12, decimal_places=2)
    subject: str | None = Field(default=None, min_length=1, max_length=200)
    person_id: int | None = Field(default=None, ge=1)
    course_id: int | None = Field(default=None, ge=1)
    description: str | None = Field(default=None, min_length=1, max_length=500)
    document_reference: str | None = Field(default=None, max_length=200)


class MovementResponse(MovementCreateRequest):
    amount: Money
    id: int
    created_at: str
    updated_at: str
    version: int


class OpeningBalancesRequest(ApiModel):
    bank: Decimal = Field(max_digits=12, decimal_places=2)
    cash: Decimal = Field(max_digits=12, decimal_places=2)


class OpeningBalancesResponse(ApiModel):
    fiscal_year: int
    bank: Money
    cash: Money


class AccountSummary(ApiModel):
    account: Account
    opening: Money
    income: Money
    expense: Money
    closing: Money


class CategorySummary(ApiModel):
    category_id: int
    direction: MovementDirection
    amount: Money


class SummaryResponse(ApiModel):
    fiscal_year: int
    accounts: list[AccountSummary]
    categories: list[CategorySummary]
