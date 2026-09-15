"""Policy/configuration for continuous paper learning across all target timeframes."""
from __future__ import annotations

TIMEFRAMES = ("1M", "5M", "15M", "30M", "1H", "2H", "4H", "1D", "1W")
ASSETS = ("BTCUSDT", "XAUUSD")
AGENTS = tuple(f"Q{i}" for i in range(1, 9))


class RealtimeTrainingPolicy:
    mode = "PAPER_REALTIME_TRAINING"
    live_execution = False
    credentials_required = False
    target_assets = ASSETS
    target_timeframes = TIMEFRAMES
    agents = AGENTS
    simulated_execution_latency_ms = 25
    additional_slippage_bps = 0.5
    live_latency_warning = (
        "Training uses observed feed/decision latency plus an explicit simulated execution delay. "
        "Live accounts can differ by milliseconds or more because of network path, broker/exchange "
        "matching, queue position, spread and market conditions. Historical paper P&L is not a "
        "guarantee of live P&L."
    )

    def snapshot(self) -> dict:
        return {
            "mode": self.mode,
            "live_execution": self.live_execution,
            "credentials_required": self.credentials_required,
            "assets": list(self.target_assets),
            "timeframes": list(self.target_timeframes),
            "agents": list(self.agents),
            "simulated_execution_latency_ms": self.simulated_execution_latency_ms,
            "additional_slippage_bps": self.additional_slippage_bps,
            "live_latency_warning": self.live_latency_warning,
        }
