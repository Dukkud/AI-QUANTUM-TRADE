"""Cost-aware research framework for AI-QUANTUM edge validation.

The module deliberately evaluates supplied research observations only. It does
not fetch market data, place orders, or change live-gate state. It is intended
to answer one question: does an added feature group improve out-of-sample
performance after explicit trading costs?
"""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Iterable, Mapping, Sequence


@dataclass(frozen=True)
class ResearchTrade:
    """One already-resolved research trade, expressed in R multiples."""

    pnl_r: float
    predicted_probability: float = 0.5
    feature_group: str = "baseline"

    def __post_init__(self) -> None:
        if not isfinite(self.pnl_r):
            raise ValueError("pnl_r must be finite")
        if not 0.0 <= self.predicted_probability <= 1.0:
            raise ValueError("predicted_probability must be between 0 and 1")
        if not self.feature_group:
            raise ValueError("feature_group is required")


@dataclass(frozen=True)
class EdgeMetrics:
    trades: int
    net_r: float
    expectancy_r: float
    win_rate: float
    profit_factor: float
    max_drawdown_r: float
    avg_win_r: float
    avg_loss_r: float
    brier_score: float

    def as_dict(self) -> dict[str, float | int]:
        return {
            "trades": self.trades,
            "net_r": round(self.net_r, 8),
            "expectancy_r": round(self.expectancy_r, 8),
            "win_rate": round(self.win_rate, 8),
            "profit_factor": round(self.profit_factor, 8),
            "max_drawdown_r": round(self.max_drawdown_r, 8),
            "avg_win_r": round(self.avg_win_r, 8),
            "avg_loss_r": round(self.avg_loss_r, 8),
            "brier_score": round(self.brier_score, 8),
        }


def _brier(trades: Sequence[ResearchTrade]) -> float:
    if not trades:
        return 0.0
    return sum((t.predicted_probability - (1.0 if t.pnl_r > 0 else 0.0)) ** 2 for t in trades) / len(trades)


def metrics(trades: Sequence[ResearchTrade], cost_r_per_trade: float = 0.0) -> EdgeMetrics:
    """Calculate net performance after a fixed cost expressed in R/trade."""
    if cost_r_per_trade < 0 or not isfinite(cost_r_per_trade):
        raise ValueError("cost_r_per_trade must be finite and non-negative")
    net = [t.pnl_r - cost_r_per_trade for t in trades]
    n = len(net)
    if not n:
        return EdgeMetrics(0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
    wins = [x for x in net if x > 0]
    losses = [x for x in net if x < 0]
    gross_profit = sum(wins)
    gross_loss = abs(sum(losses))
    equity = peak = 0.0
    max_dd = 0.0
    for x in net:
        equity += x
        peak = max(peak, equity)
        max_dd = max(max_dd, peak - equity)
    return EdgeMetrics(
        trades=n,
        net_r=sum(net),
        expectancy_r=sum(net) / n,
        win_rate=len(wins) / n,
        profit_factor=(gross_profit / gross_loss) if gross_loss else (float("inf") if gross_profit else 0.0),
        max_drawdown_r=max_dd,
        avg_win_r=(sum(wins) / len(wins)) if wins else 0.0,
        avg_loss_r=(sum(losses) / len(losses)) if losses else 0.0,
        brier_score=_brier(trades),
    )


def _coerce_trades(rows: Iterable[Mapping[str, object]], feature_group: str) -> list[ResearchTrade]:
    return [
        ResearchTrade(
            pnl_r=float(row["pnl_r"]),
            predicted_probability=float(row.get("predicted_probability", 0.5)),
            feature_group=feature_group,
        )
        for row in rows
    ]


def feature_attribution(
    variants: Mapping[str, Iterable[Mapping[str, object]]],
    cost_r_per_trade: float = 0.0,
) -> dict[str, object]:
    """Compare baseline and feature variants using identical cost assumptions."""
    if "baseline" not in variants:
        raise ValueError("variants must include baseline")
    evaluated: dict[str, EdgeMetrics] = {
        name: metrics(_coerce_trades(rows, name), cost_r_per_trade)
        for name, rows in variants.items()
    }
    base = evaluated["baseline"]
    ranking = []
    for name, result in evaluated.items():
        ranking.append(
            {
                "feature_group": name,
                "net_r_delta_vs_baseline": round(result.net_r - base.net_r, 8),
                "expectancy_delta_vs_baseline": round(result.expectancy_r - base.expectancy_r, 8),
                "max_drawdown_delta_vs_baseline": round(result.max_drawdown_r - base.max_drawdown_r, 8),
                "metrics": result.as_dict(),
            }
        )
    ranking.sort(key=lambda x: (x["net_r_delta_vs_baseline"], x["expectancy_delta_vs_baseline"]), reverse=True)
    return {"cost_r_per_trade": cost_r_per_trade, "baseline": base.as_dict(), "ranking": ranking}


def walk_forward(
    trades: Sequence[ResearchTrade],
    train_size: int,
    validation_size: int,
    oos_size: int,
    cost_r_per_trade: float = 0.0,
) -> list[dict[str, object]]:
    """Create causal sequential train/validation/OOS windows without shuffling."""
    if min(train_size, validation_size, oos_size) <= 0:
        raise ValueError("window sizes must be positive")
    width = train_size + validation_size + oos_size
    windows: list[dict[str, object]] = []
    start = 0
    fold = 1
    while start + width <= len(trades):
        train = trades[start : start + train_size]
        validation = trades[start + train_size : start + train_size + validation_size]
        oos = trades[start + train_size + validation_size : start + width]
        windows.append(
            {
                "fold": fold,
                "train": metrics(train, cost_r_per_trade).as_dict(),
                "validation": metrics(validation, cost_r_per_trade).as_dict(),
                "oos": metrics(oos, cost_r_per_trade).as_dict(),
            }
        )
        start += oos_size
        fold += 1
    return windows


def validation_gate(
    oos_metrics: Sequence[Mapping[str, object]],
    min_trades: int = 30,
    min_expectancy_r: float = 0.0,
    max_drawdown_r: float = 10.0,
    max_brier: float = 0.25,
) -> dict[str, object]:
    """Fail-closed promotion gate for research candidates."""
    checks = {
        "minimum_trades": all(int(x["trades"]) >= min_trades for x in oos_metrics) if oos_metrics else False,
        "positive_expectancy": all(float(x["expectancy_r"]) > min_expectancy_r for x in oos_metrics) if oos_metrics else False,
        "drawdown_limit": all(float(x["max_drawdown_r"]) <= max_drawdown_r for x in oos_metrics) if oos_metrics else False,
        "calibration": all(float(x["brier_score"]) <= max_brier for x in oos_metrics) if oos_metrics else False,
    }
    return {
        "status": "PROMOTE" if all(checks.values()) else "HOLD",
        "checks": checks,
        "live_execution": False,
        "research_only": True,
    }
