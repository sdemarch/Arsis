"""RB-22: dates of recurring activities."""

from datetime import date

import pytest

from arsis.activities.recurrence import RecurrenceError, build_rule, describe, occurrence_dates


def _dates(**kwargs: object) -> list[str]:
    return [day.isoformat() for day in occurrence_dates(build_rule(**kwargs))]  # type: ignore[arg-type]


def test_weekly_on_two_weekdays() -> None:
    # 2026-12-01 is a Tuesday.
    assert _dates(
        frequency="weekly",
        interval=1,
        starts_on=date(2026, 12, 1),
        ends_on=date(2026, 12, 11),
        weekdays=[5, 2],
    ) == ["2026-12-01", "2026-12-04", "2026-12-08", "2026-12-11"]


def test_weekly_skips_days_before_start_and_respects_interval() -> None:
    # Starts on Wednesday: that week's Tuesday is skipped; every other week.
    assert _dates(
        frequency="weekly",
        interval=2,
        starts_on=date(2026, 12, 2),
        ends_on=date(2026, 12, 31),
        weekdays=[2],
    ) == ["2026-12-15", "2026-12-29"]


def test_monthly_skips_months_without_the_day() -> None:
    assert _dates(
        frequency="monthly",
        interval=1,
        starts_on=date(2027, 1, 31),
        ends_on=date(2027, 5, 31),
        weekdays=None,
    ) == ["2027-01-31", "2027-03-31", "2027-05-31"]


def test_monthly_interval_crosses_the_year() -> None:
    assert _dates(
        frequency="monthly",
        interval=3,
        starts_on=date(2026, 11, 15),
        ends_on=date(2027, 8, 15),
        weekdays=None,
    ) == ["2026-11-15", "2027-02-15", "2027-05-15", "2027-08-15"]


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"weekdays": []}, "almeno un giorno"),
        ({"weekdays": [8]}, "non valido"),
        ({"ends_on": date(2026, 11, 30)}, "fine"),
        ({"ends_on": date(2028, 1, 1)}, "un anno"),
        ({"interval": 13}, "intervallo"),
    ],
)
def test_invalid_rules(kwargs: dict[str, object], message: str) -> None:
    rule = {
        "frequency": "weekly",
        "interval": 1,
        "starts_on": date(2026, 12, 1),
        "ends_on": date(2026, 12, 31),
        "weekdays": [2],
        **kwargs,
    }
    with pytest.raises(RecurrenceError, match=message):
        occurrence_dates(build_rule(**rule))  # type: ignore[arg-type]


def test_too_many_occurrences() -> None:
    rule = build_rule(
        frequency="weekly",
        interval=1,
        starts_on=date(2026, 1, 1),
        ends_on=date(2026, 12, 31),
        weekdays=[1, 2, 3, 4, 5],
    )
    with pytest.raises(RecurrenceError, match="al massimo 200"):
        occurrence_dates(rule)


def test_description() -> None:
    weekly = build_rule(
        frequency="weekly",
        interval=2,
        starts_on=date(2026, 12, 1),
        ends_on=date(2026, 12, 31),
        weekdays=[5, 2],
    )
    assert describe(weekly) == "Ogni 2 settimane: martedì, venerdì"
    monthly = build_rule(
        frequency="monthly",
        interval=1,
        starts_on=date(2026, 12, 6),
        ends_on=date(2027, 6, 6),
        weekdays=None,
    )
    assert describe(monthly) == "Ogni mese, il giorno 6"
