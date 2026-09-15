from src.edge_validation import ResearchTrade, feature_attribution, metrics, validation_gate, walk_forward


def test_metrics_are_cost_aware_and_deterministic():
    trades = [ResearchTrade(1.0, 0.8), ResearchTrade(-0.5, 0.2), ResearchTrade(0.5, 0.7)]
    result = metrics(trades, cost_r_per_trade=0.1)
    assert result.trades == 3
    assert abs(result.net_r - 0.7) < 1e-12
    assert result.win_rate == 2 / 3
    assert result.profit_factor > 1
    assert abs(result.max_drawdown_r - 0.6) < 1e-12


def test_feature_attribution_ranks_positive_incremental_edge():
    variants = {
        "baseline": [
            {"pnl_r": 0.4, "predicted_probability": 0.6},
            {"pnl_r": -0.2, "predicted_probability": 0.4},
            {"pnl_r": 0.3, "predicted_probability": 0.7},
        ],
        "pine": [
            {"pnl_r": 0.6, "predicted_probability": 0.7},
            {"pnl_r": -0.1, "predicted_probability": 0.35},
            {"pnl_r": 0.5, "predicted_probability": 0.75},
        ],
        "midas": [
            {"pnl_r": 0.2, "predicted_probability": 0.55},
            {"pnl_r": -0.3, "predicted_probability": 0.45},
            {"pnl_r": 0.1, "predicted_probability": 0.55},
        ],
    }
    result = feature_attribution(variants, cost_r_per_trade=0.05)
    assert result["ranking"][0]["feature_group"] == "pine"
    assert result["ranking"][0]["net_r_delta_vs_baseline"] > 0


def test_walk_forward_is_causal_and_sequential():
    trades = [ResearchTrade(0.1 if i % 2 == 0 else -0.05, 0.6 if i % 2 == 0 else 0.4) for i in range(14)]
    windows = walk_forward(trades, train_size=4, validation_size=2, oos_size=2)
    assert len(windows) == 4
    assert [w["fold"] for w in windows] == [1, 2, 3, 4]
    assert all("oos" in w for w in windows)


def test_validation_gate_fails_closed_on_insufficient_or_bad_oos():
    good = {"trades": 30, "expectancy_r": 0.1, "max_drawdown_r": 2.0, "brier_score": 0.12}
    bad = {"trades": 10, "expectancy_r": -0.1, "max_drawdown_r": 20.0, "brier_score": 0.4}
    assert validation_gate([good])["status"] == "PROMOTE"
    blocked = validation_gate([bad])
    assert blocked["status"] == "HOLD"
    assert blocked["live_execution"] is False


def test_empty_oos_never_promotes():
    result = validation_gate([])
    assert result["status"] == "HOLD"
