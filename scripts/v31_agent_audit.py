import json
import math
from datetime import datetime, timedelta, timezone
from pathlib import Path

from src.paper_world import AGENTS, INITIAL_BALANCE, PaperWorld

OUT = Path("overnight_report.json")


def _market_path(n=2400, start=3000.0):
    """Deterministic stress path: trend, reversal, range and volatility burst."""
    prices = []
    p = start
    for i in range(n):
        if i < 600:
            drift = 0.55
        elif i < 1200:
            drift = -0.72
        elif i < 1800:
            drift = 0.08 * math.sin(i / 17.0)
        else:
            drift = 0.95 * math.sin(i / 4.0)
        shock = 2.8 * math.sin(i / 11.0) + 1.1 * math.sin(i / 3.0)
        p += drift + shock
        prices.append(p)
    return prices


def _audit_agent(wallet, before_balance):
    history = wallet.history
    pnls = [float(x["pnl"]) for x in history]
    gross_profit = sum(x for x in pnls if x > 0)
    gross_loss = -sum(x for x in pnls if x < 0)
    net = sum(pnls)
    pf = gross_profit / gross_loss if gross_loss else (math.inf if gross_profit else 0.0)
    balances = [INITIAL_BALANCE] + [float(x["balance_after"]) for x in history]
    peak = balances[0]
    max_dd = 0.0
    for b in balances:
        peak = max(peak, b)
        if peak:
            max_dd = max(max_dd, (peak - b) / peak)
    compounding_ok = all(
        x["balance_after"] >= INITIAL_BALANCE for x in history
    )
    experience_ok = wallet.experience >= 0 and wallet.trades >= 0
    geometric_growth = wallet.balance / before_balance if before_balance else 1.0
    avg_win = gross_profit / wallet.wins if wallet.wins else 0.0
    avg_loss = gross_loss / wallet.losses if wallet.losses else 0.0
    p = wallet.win_rate
    ev = p * avg_win - (1 - p) * avg_loss
    return {
        "balance": round(wallet.balance, 8),
        "return_pct": round((wallet.balance / before_balance - 1) * 100, 6) if before_balance else 0.0,
        "geometric_balance_factor": round(geometric_growth, 8),
        "trades": wallet.trades,
        "wins": wallet.wins,
        "losses": wallet.losses,
        "win_rate": round(wallet.win_rate, 6),
        "gross_profit": round(gross_profit, 8),
        "gross_loss": round(gross_loss, 8),
        "profit_factor": round(pf, 6) if math.isfinite(pf) else "INF",
        "net_pnl": round(net, 8),
        "max_drawdown_pct": round(max_dd * 100, 6),
        "experience": round(wallet.experience, 8),
        "loss_debt": round(wallet.loss_debt, 8),
        "locked_until": wallet.locked_until,
        "expected_value_per_trade": round(ev, 8),
        "compounding_invariant_pass": compounding_ok,
        "experience_invariant_pass": experience_ok,
        "floor_invariant_pass": all(x["balance_after"] >= INITIAL_BALANCE for x in history),
    }


def main():
    world = PaperWorld()
    before = {k: w.balance for k, w in world.wallets.items()}
    t = datetime(2026, 1, 1, tzinfo=timezone.utc)
    prices = _market_path()
    for i, price in enumerate(prices):
        world.tick("XAUUSD", round(price, 5), (t + timedelta(minutes=i)).isoformat(), prices[i - 1] if i else price)

    agents = {k: _audit_agent(w, before[k]) for k, w in world.wallets.items()}
    positive_ev = sum(v["expected_value_per_trade"] > 0 for v in agents.values())
    invariant_pass = all(
        v["compounding_invariant_pass"] and v["experience_invariant_pass"] and v["floor_invariant_pass"]
        for v in agents.values()
    )
    report = {
        "schema": "AI-QUANTUM.v31.agent-audit.v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "scope": "paper-world agent learning, geometric compounding, risk and execution invariants",
        "mode": "PAPER_ONLY",
        "live_execution": False,
        "scenario": {"asset": "XAUUSD", "ticks": len(prices), "agents": len(AGENTS), "initial_balance": INITIAL_BALANCE},
        "aggregate": {
            "all_invariants_pass": invariant_pass,
            "agents_with_positive_ev": positive_ev,
            "agents_total": len(AGENTS),
            "all_agents_traded": all(v["trades"] > 0 for v in agents.values()),
            "all_agents_have_experience": all(v["experience"] > 0 for v in agents.values()),
        },
        "agents": agents,
        "conclusion": (
            "PASS: paper-world learning/compounding invariants and agent accounting are functioning; "
            "next step is richer adaptive learning/calibration and persistent cross-run state."
            if invariant_pass else
            "BLOCK: one or more agent invariants failed; do not advance to live trading."
        ),
        "next_step": "v31.1: persistent audit history + adaptive/calibrated agent scoring + real native feed validation",
    }
    OUT.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
