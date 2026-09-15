"""Evidence gate for AI-QUANTUM research milestones.

This layer is deliberately stricter than the numerical edge gate. A positive
backtest is not sufficient evidence for promotion: the candidate must also
provide provenance, cost realism, leakage controls, multiple OOS windows and
forward paper evidence. The gate can only promote a research candidate; it
cannot enable live execution.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence


@dataclass(frozen=True)
class EvidenceRequirements:
    real_historical_data: bool = False
    versioned_data: bool = False
    native_quotes_or_defensible_cost_model: bool = False
    causal_timestamps: bool = False
    no_leakage_verified: bool = False
    multiple_oos_windows: bool = False
    regime_robustness: bool = False
    calibration_acceptable: bool = False
    positive_net_expectancy_after_costs: bool = False
    forward_paper_validation: bool = False
    independent_review: bool = False

    def as_dict(self) -> dict[str, bool]:
        return {
            "real_historical_data": self.real_historical_data,
            "versioned_data": self.versioned_data,
            "native_quotes_or_defensible_cost_model": self.native_quotes_or_defensible_cost_model,
            "causal_timestamps": self.causal_timestamps,
            "no_leakage_verified": self.no_leakage_verified,
            "multiple_oos_windows": self.multiple_oos_windows,
            "regime_robustness": self.regime_robustness,
            "calibration_acceptable": self.calibration_acceptable,
            "positive_net_expectancy_after_costs": self.positive_net_expectancy_after_costs,
            "forward_paper_validation": self.forward_paper_validation,
            "independent_review": self.independent_review,
        }


def evidence_gate(
    evidence: EvidenceRequirements | Mapping[str, object],
    oos_metrics: Sequence[Mapping[str, object]] | None = None,
) -> dict[str, object]:
    """Fail closed unless every required research evidence item is present."""
    if isinstance(evidence, EvidenceRequirements):
        checks = evidence.as_dict()
    else:
        checks = EvidenceRequirements(**{
            key: bool(evidence.get(key, False))
            for key in EvidenceRequirements.__dataclass_fields__
        }).as_dict()

    if oos_metrics is None or len(oos_metrics) < 2:
        checks["multiple_oos_windows"] = False

    if oos_metrics:
        checks["positive_net_expectancy_after_costs"] = checks["positive_net_expectancy_after_costs"] and all(
            float(row.get("expectancy_r", 0.0)) > 0.0 for row in oos_metrics
        )
        checks["calibration_acceptable"] = checks["calibration_acceptable"] and all(
            float(row.get("brier_score", 1.0)) <= 0.25 for row in oos_metrics
        )

    return {
        "status": "PROMOTE_RESEARCH" if all(checks.values()) else "HOLD",
        "checks": checks,
        "research_only": True,
        "live_execution": False,
        "live_gate_enablement": False,
    }
