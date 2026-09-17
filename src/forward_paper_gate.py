"""Forward-paper settlement gate; observational only."""
from __future__ import annotations
from dataclasses import dataclass
from math import isfinite

@dataclass(frozen=True)
class PaperStats:
    samples: int
    net_r: float
    max_drawdown_r: float
    settled_fraction: float

@dataclass(frozen=True)
class PaperGate:
    status: str
    blockers: tuple[str, ...]

def evaluate_forward_paper(stats: PaperStats, *, min_samples=100, min_net_r=0.0, max_dd_r=5.0, min_settled=.99) -> PaperGate:
    if stats.samples < 0 or not all(isfinite(float(x)) for x in (stats.net_r, stats.max_drawdown_r, stats.settled_fraction)):
        raise ValueError('invalid paper statistics')
    blockers=[]
    if stats.samples < min_samples: blockers.append('SAMPLE_COUNT')
    if stats.net_r < min_net_r: blockers.append('NET_R')
    if stats.max_drawdown_r > max_dd_r: blockers.append('MAX_DRAWDOWN_R')
    if not 0 <= stats.settled_fraction <= 1 or stats.settled_fraction < min_settled: blockers.append('SETTLEMENT_COMPLETENESS')
    return PaperGate('PASS' if not blockers else 'REVIEW', tuple(blockers))
