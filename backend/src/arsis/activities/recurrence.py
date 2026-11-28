"""Dates of a recurring activity (RB-22).

Pure date arithmetic on local calendar dates: the browser turns each date into a
timestamp with the right UTC offset, so daylight saving never shifts an occurrence.
"""

import calendar
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Literal

Frequency = Literal["weekly", "monthly"]

MAX_OCCURRENCES = 200
MAX_SPAN_DAYS = 366


class RecurrenceError(ValueError):
    """A rule that cannot produce a valid set of occurrences."""


@dataclass(frozen=True)
class RecurrenceRule:
    frequency: Frequency
    interval: int
    starts_on: date
    ends_on: date
    weekdays: tuple[int, ...] = ()  # ISO: 1 = Monday ... 7 = Sunday; weekly only

    def weekdays_text(self) -> str | None:
        return ",".join(str(day) for day in self.weekdays) if self.frequency == "weekly" else None


def build_rule(
    *,
    frequency: Frequency,
    interval: int,
    starts_on: date,
    ends_on: date,
    weekdays: list[int] | tuple[int, ...] | None,
) -> RecurrenceRule:
    if not 1 <= interval <= 12:
        raise RecurrenceError("L'intervallo deve essere tra 1 e 12")
    if ends_on < starts_on:
        raise RecurrenceError("La data di fine deve seguire la data di inizio")
    if (ends_on - starts_on).days > MAX_SPAN_DAYS:
        raise RecurrenceError("Una serie può coprire al massimo un anno")
    days: tuple[int, ...] = ()
    if frequency == "weekly":
        days = tuple(sorted(set(weekdays or ())))
        if not days:
            raise RecurrenceError("Scegli almeno un giorno della settimana")
        if any(day < 1 or day > 7 for day in days):
            raise RecurrenceError("Giorno della settimana non valido")
    return RecurrenceRule(frequency, interval, starts_on, ends_on, days)


def occurrence_dates(rule: RecurrenceRule) -> list[date]:
    """Dates from ``starts_on`` to ``ends_on`` included, in order."""
    dates = _weekly(rule) if rule.frequency == "weekly" else _monthly(rule)
    if not dates:
        raise RecurrenceError("La regola non produce nessuna attività nel periodo indicato")
    if len(dates) > MAX_OCCURRENCES:
        raise RecurrenceError(f"Una serie può contenere al massimo {MAX_OCCURRENCES} attività")
    return dates


def _weekly(rule: RecurrenceRule) -> list[date]:
    # Weeks are counted from the Monday of the first week, every ``interval`` weeks.
    monday = rule.starts_on - timedelta(days=rule.starts_on.isoweekday() - 1)
    dates: list[date] = []
    while monday <= rule.ends_on:
        for day in rule.weekdays:
            current = monday + timedelta(days=day - 1)
            if rule.starts_on <= current <= rule.ends_on:
                dates.append(current)
        monday += timedelta(weeks=rule.interval)
    return dates


def _monthly(rule: RecurrenceRule) -> list[date]:
    # Same day of month as the first date; months without that day are skipped
    # (a series on the 31st has no occurrence in April).
    day = rule.starts_on.day
    year, month = rule.starts_on.year, rule.starts_on.month
    dates: list[date] = []
    while date(year, month, 1) <= rule.ends_on:
        if day <= calendar.monthrange(year, month)[1]:
            current = date(year, month, day)
            if rule.starts_on <= current <= rule.ends_on:
                dates.append(current)
        month += rule.interval
        year, month = year + (month - 1) // 12, (month - 1) % 12 + 1
    return dates


def describe(rule: RecurrenceRule) -> str:
    """Italian summary, e.g. 'Ogni 2 settimane: martedì, venerdì'."""
    names = ["lunedì", "martedì", "mercoledì", "giovedì", "venerdì", "sabato", "domenica"]
    if rule.frequency == "weekly":
        every = "Ogni settimana" if rule.interval == 1 else f"Ogni {rule.interval} settimane"
        return f"{every}: {', '.join(names[day - 1] for day in rule.weekdays)}"
    every = "Ogni mese" if rule.interval == 1 else f"Ogni {rule.interval} mesi"
    return f"{every}, il giorno {rule.starts_on.day}"
