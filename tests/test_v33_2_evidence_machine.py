from src.evidence_machine import EvidenceMachine


def test_shadow_evidence_does_not_require_q3_q6_q7_to_keep_observing():
    machine = EvidenceMachine()
    out = machine.observe(asset='BTCUSDT', price=100.0, timestamp='2026-01-01T00:00:00+00:00')
    assert out['research_only'] is True
    assert out['live_execution'] is False
    assert machine.snapshot()['events'] == 1
    assert machine.snapshot()['latest_shadow'] is not None


def test_ml_prediction_is_recorded_and_settled_causally():
    machine = EvidenceMachine()
    machine.observe(asset='BTCUSDT', price=100.0, timestamp='2026-01-01T00:00:00+00:00',
                    payload={'ml_probability': 0.8, 'model_version': 'm1', 'ml_calibrated': True})
    machine.observe(asset='BTCUSDT', price=101.0, timestamp='2026-01-01T00:01:00+00:00')
    assert machine.snapshot()['predictions'] == 1
    assert machine.snapshot()['settled_predictions'] == 1
    assert abs(machine.brier() - 0.04) < 1e-12


def test_invalid_probability_is_rejected():
    machine = EvidenceMachine()
    try:
        machine.observe(asset='BTCUSDT', price=100.0, payload={'ml_probability': 1.2})
    except ValueError as exc:
        assert 'ml_probability' in str(exc)
    else:
        raise AssertionError('invalid probability must fail closed')
