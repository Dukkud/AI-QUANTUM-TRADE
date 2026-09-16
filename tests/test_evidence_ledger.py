from src.evidence_ledger import EvidenceLedger, PredictionEvidence, GENESIS


def sample(i="p1"):
    return PredictionEvidence(
        prediction_id=i,
        observed_at_utc="2026-09-16T10:00:00Z",
        asset="XAUUSD",
        timeframe="1H",
        decision="APPROVE",
        direction="LONG",
        entry=2500.0,
        stop=2490.0,
        target=2520.0,
        probability=0.62,
        agent_outputs={"Q1": {"regime": "trend"}, "Q7": {"confidence": 0.7}},
        data_quality=0.99,
    )


def test_empty_ledger_is_valid(tmp_path):
    ok, count, tail = EvidenceLedger(tmp_path / "evidence.jsonl").verify()
    assert (ok, count, tail) == (True, 0, GENESIS)


def test_append_and_verify_chain(tmp_path):
    path = tmp_path / "evidence.jsonl"
    ledger = EvidenceLedger(path)
    first = ledger.append(sample())
    second = ledger.append(sample("p2"))
    assert first != second
    ok, count, tail = ledger.verify()
    assert ok is True
    assert count == 2
    assert tail == second


def test_tampering_is_detected(tmp_path):
    path = tmp_path / "evidence.jsonl"
    ledger = EvidenceLedger(path)
    ledger.append(sample())
    raw = path.read_text(encoding="utf-8")
    path.write_text(raw.replace('"probability":0.62', '"probability":0.92'), encoding="utf-8")
    ok, count, reason = ledger.verify()
    assert ok is False
    assert count == 1
    assert reason == "record_hash mismatch"


def test_prediction_id_required(tmp_path):
    ledger = EvidenceLedger(tmp_path / "evidence.jsonl")
    evidence = sample("")
    try:
        ledger.append(evidence)
        assert False
    except ValueError as exc:
        assert "prediction_id" in str(exc)
