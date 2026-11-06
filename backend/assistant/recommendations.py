"""Rule-based reduction recommendations with indicative savings estimates.

Savings are calculated deterministically here, never by the language model, so the
numbers are reproducible and testable. ``reduction_share`` is a conservative typical
share of the scope's emissions that the measure can avoid for an SME.
"""

from dataclasses import asdict, dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Measure:
    key: str
    scope: int
    title: str
    description: str
    reduction_share: Decimal
    effort: str


@dataclass(frozen=True)
class Recommendation:
    key: str
    scope: int
    title: str
    description: str
    effort: str
    reduction_share: Decimal
    estimated_savings_kg_co2e: Decimal

    def as_dict(self):
        return {k: str(v) if isinstance(v, Decimal) else v for k, v in asdict(self).items()}


CATALOGUE = (
    Measure(
        "heating_optimisation",
        1,
        "Optimise heating",
        "Tune heating schedules and thermostats, service boilers and seal draughts.",
        Decimal("0.10"),
        "low",
    ),
    Measure(
        "fleet_electrification",
        1,
        "Electrify company vehicles",
        "Replace combustion vehicles with electric ones at the end of their lease.",
        Decimal("0.25"),
        "high",
    ),
    Measure(
        "renewable_electricity",
        2,
        "Switch to renewable electricity",
        "Move to a certified green electricity tariff or install on-site solar.",
        Decimal("0.70"),
        "low",
    ),
    Measure(
        "efficient_lighting",
        2,
        "LED lighting and smart controls",
        "Replace remaining lamps with LEDs and add occupancy sensors.",
        Decimal("0.08"),
        "medium",
    ),
    Measure(
        "equipment_shutdown",
        2,
        "Switch-off policy for equipment",
        "Power down IT, machines and HVAC outside working hours.",
        Decimal("0.05"),
        "low",
    ),
    Measure(
        "travel_policy",
        3,
        "Rail-first travel policy",
        "Prefer rail over short-haul flights and replace routine trips with video calls.",
        Decimal("0.15"),
        "low",
    ),
    Measure(
        "supplier_engagement",
        3,
        "Engage key suppliers",
        "Ask the largest suppliers for emissions data and favour lower-carbon options.",
        Decimal("0.10"),
        "medium",
    ),
    Measure(
        "commuting",
        3,
        "Low-carbon commuting",
        "Offer public transport tickets, bike leasing and remote-work days.",
        Decimal("0.05"),
        "medium",
    ),
)


def recommend(totals: dict[int, Decimal], limit: int = 5) -> list[Recommendation]:
    """Rank measures by estimated savings for the given kg CO2e totals per scope."""
    ranked = []
    for measure in CATALOGUE:
        scope_total = Decimal(totals.get(measure.scope, 0))
        savings = (scope_total * measure.reduction_share).quantize(Decimal("0.01"))
        if savings > 0:
            ranked.append(
                Recommendation(
                    key=measure.key,
                    scope=measure.scope,
                    title=measure.title,
                    description=measure.description,
                    effort=measure.effort,
                    reduction_share=measure.reduction_share,
                    estimated_savings_kg_co2e=savings,
                )
            )
    ranked.sort(key=lambda item: item.estimated_savings_kg_co2e, reverse=True)
    return ranked[:limit]
