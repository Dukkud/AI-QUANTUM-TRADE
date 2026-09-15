from src.evidence_gate import EvidenceRequirements, evidence_gate


def test_evidence_gate_requires_multiple_oos_windows():
    evidence = EvidenceRequirements(
        real_historical_data=True,
        versioned_data=True,
        native_quotes_or_defensible_cost_model=True,
        causal_timestamps=True,
        no_leakage_verified=True,
        multiple_oos_windows=True,
        regime_robustness=True,
        calibration_acceptable=True,
        positive_net_expectancy_after_costs=True,
        forward_paper_validation=True,
        independent_review=True,
    )
    one_window = [{"expectancy_r": 0.1, "brier_score": 0.1}]
    assert evidence_gate(evidence, one_window)["status"] == "HOLD"


def test_evidence_gate_promotes_only_complete_research_evidence():
    evidence = EvidenceRequirements(
        real_historical_data=True,
        versioned_data=True,
        native_quotes_or_defensible_cost_model=True,
        causal_timestamps=True,
        no_leakage_verified=True,
        multiple_oos_windows=True,
        regime_robustness=True,
        calibration_acceptable=True,
        positive_net_expectancy_after_costs=True,
        forward_paper_validation=True,
        independent_review=True,
    )
    oos = [
        {"expectancy_r": 0.12, "brier_score": 0.10},
        {"expectancy_r": 0.07, "brier_score": 0.18},
    ]
    result = evidence_gate(evidence, oos)
    assert result["status"] == "PROMOTE_RESEARCH"
    assert result["live_execution"] is False
    assert result["live_gate_enablement"] is False


def test_evidence_gate_blocks_bad_oos_even_if_flags_are_true():
    evidence = EvidenceRequirements(
        real_historical_data=True,
        versioned_data=True,
        native_quotes_or_defensible_cost_model=True,
        causal_timestamps=True,
        no_leakage_verified=True,
        multiple_oos_windows=True,
        regime_robustness=True,
        calibration_acceptable=True,
        positive_net_expectancy_after_costs=True,
        forward_paper_validation=True,
        independent_review=True,
    )
    oos = [
        {"expectancy_r": 0.12, "brier_score": 0.10},
        {"expectancy_r": -0.02, "brier_score": 0.18},
    ]
    assert evidence_gate(evidence, oos)["status"] == "HOLD"
