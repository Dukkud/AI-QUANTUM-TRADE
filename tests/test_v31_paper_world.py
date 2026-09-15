from datetime import datetime, timezone, timedelta
from src.paper_world import PaperWorld, AGENTS, INITIAL_BALANCE
from src.live_gate import ClientLiveGate


def test_eight_wallets_start_at_1000():
    world = PaperWorld()
    assert set(world.wallets) == set(AGENTS)
    assert all(w.balance == INITIAL_BALANCE for w in world.wallets.values())


def test_trade_lines_and_position_created():
    world = PaperWorld()
    snap = world.tick('XAUUSD', 3000.0, '2026-01-01T00:00:00+00:00', 2990.0)
    assert len(snap['lines']) == 8
    assert all(len(w.positions) == 1 for w in world.wallets.values())


def test_take_profit_records_pnl_and_experience():
    world = PaperWorld()
    world.tick('XAUUSD', 3000.0, '2026-01-01T00:00:00+00:00', 2990.0)
    world.tick('XAUUSD', 3010.0, '2026-01-01T00:01:00+00:00', 3000.0)
    assert all(w.trades == 1 for w in world.wallets.values())
    assert all(w.wins == 1 for w in world.wallets.values())
    assert all(w.experience > 0 for w in world.wallets.values())


def test_five_day_recovery_cycle():
    world = PaperWorld()
    wallet = world.wallets['Q1']
    wallet.balance = -1.0
    wallet.locked_until = (world.clock + timedelta(days=5)).isoformat()
    assert wallet.is_locked(world.clock)
    world.clock = world.clock + timedelta(days=5)
    assert world.unlock_after_review('Q1') is True
    assert wallet.balance == INITIAL_BALANCE
    assert wallet.locked_until is None


def test_live_gate_requires_verified_account_and_explicit_confirmation():
    gate = ClientLiveGate()
    gate.register('demo-1', 'MT5')
    all_ok = {k: True for k in ['real_data_verified','data_quality_pass','reconciliation_pass','paper_execution_pass','risk_engine_pass']}
    assert gate.can_trade_live('demo-1', all_ok, live_trading=True, emergency_stop=False) is False
    gate.verify('demo-1')
    assert gate.can_trade_live('demo-1', all_ok, live_trading=True, emergency_stop=False) is False
    gate.confirm_trading('demo-1')
    assert gate.can_trade_live('demo-1', all_ok, live_trading=True, emergency_stop=False) is True


def test_live_gate_fails_if_any_safety_gate_is_missing():
    gate = ClientLiveGate()
    gate.register('demo-2', 'MT5')
    gate.verify('demo-2')
    gate.confirm_trading('demo-2')
    gates = {k: True for k in ['real_data_verified','data_quality_pass','reconciliation_pass','paper_execution_pass','risk_engine_pass']}
    gates['reconciliation_pass'] = False
    assert gate.can_trade_live('demo-2', gates, live_trading=True, emergency_stop=False) is False
