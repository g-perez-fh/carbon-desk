"""Read-only seam between the emissions subsystem and its consumers.

Targets, the assistant and analytics read emission totals through this module
instead of importing emissions models, so each subsystem can evolve on its own.

Contract for ``emissions.services`` (owned by the emissions subsystem)::

    def totals_by_scope(organisation, start: date, end: date) -> dict[int, Decimal]

It returns kg CO2e per scope (1, 2, 3) for activities dated ``start <= d < end``.
Until that function exists, every total is reported as zero.
"""

from datetime import date
from decimal import Decimal

SCOPES = (1, 2, 3)


def totals_by_scope(organisation, start: date, end: date) -> dict[int, Decimal]:
    from emissions import services

    provider = getattr(services, "totals_by_scope", None)
    raw = provider(organisation, start, end) if provider else {}
    return {scope: Decimal(str(raw.get(scope) or 0)) for scope in SCOPES}


def total(totals: dict[int, Decimal], scope: str = "all") -> Decimal:
    """Sum all scopes, or pick one scope given as "1", "2" or "3"."""
    if scope == "all":
        return sum(totals.values(), Decimal("0"))
    return totals.get(int(scope), Decimal("0"))


def year_range(year: int) -> tuple[date, date]:
    return date(year, 1, 1), date(year + 1, 1, 1)


def month_range(month: date) -> tuple[date, date]:
    start = month.replace(day=1)
    end = date(start.year + start.month // 12, start.month % 12 + 1, 1)
    return start, end


def previous_month(month: date) -> date:
    start = month.replace(day=1)
    return date(start.year - 1, 12, 1) if start.month == 1 else start.replace(month=start.month - 1)
