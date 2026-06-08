from datetime import date, timedelta


def is_scaduto(d: date) -> bool:
    return d < date.today()


def is_in_scadenza(d: date, giorni: int = 30) -> bool:
    return date.today() <= d <= date.today() + timedelta(days=giorni)
