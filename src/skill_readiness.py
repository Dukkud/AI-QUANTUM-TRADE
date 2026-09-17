from __future__ import annotations
from dataclasses import dataclass

CRITICAL = (
    "registry", "governor", "provenance", "attribution", "oos",
    "budget", "sandbox", "recovery", "drift",
)

@dataclass(frozen=True)
class Readiness:
    status: str
    coverage: float
    blockers: tuple[str, ...]

def readiness(gates: dict[str, bool], required_coverage: float = 0.99) -> Readiness:
    if not 0 <= required_coverage <= 1:
        raise ValueError("required_coverage")
    coverage = sum(bool(gates.get(name, False)) for name in CRITICAL) / len(CRITICAL)
    blockers = tuple(name for name in CRITICAL if not gates.get(name, False))
    ok = coverage >= required_coverage and not blockers
    return Readiness("PASS" if ok else "BLOCKED", coverage, blockers)
