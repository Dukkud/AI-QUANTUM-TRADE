from src.pine_export import PineExporter, TFDecision, TIMEFRAMES

def sample():
    return {tf: TFDecision("APPROVE" if tf in ("1H","4H") else "WAIT", "LONG" if tf in ("1H","4H") else "FLAT", .8, .75, 2500, 2480, 2520, 2540, 2560) for tf in TIMEFRAMES}

def test_exports_two_variants_and_all_timeframes():
    a,b=PineExporter(symbol="XAUUSD",generated_at="2026-09-22T11:00:00Z").export_both(sample())
    assert a.variant == "V1_SIGNAL_MATRIX"
    assert b.variant == "V2_INSTITUTIONAL_CONFLUENCE"
    for key in ("D_1m","D_5m","D_15m","D_30m","D_1h","D_2h","D_4h","D_1d","D_1w"):
        assert key in a.content
    assert a.content.startswith("//@version=6")
    assert b.content.startswith("//@version=6")
    assert len(a.checksum)==64 and len(b.checksum)==64

def test_export_refuses_incomplete_or_invalid_final_conclusion():
    d=sample(); d.pop("1W")
    try: PineExporter(symbol="BTCUSDT",generated_at="x").variant_1(d)
    except ValueError as e: assert str(e).startswith("missing_timeframes:")
    else: assert False
    d=sample(); d["1H"]=TFDecision("BAD","LONG")
    try: PineExporter(symbol="BTCUSDT",generated_at="x").variant_1(d)
    except ValueError as e: assert "invalid_decision" in str(e)
    else: assert False

def test_no_order_execution_commands():
    a,b=PineExporter(symbol="XAUUSD",generated_at="x").export_both(sample())
    for code in (a.content,b.content):
        assert "strategy.entry" not in code
        assert "strategy.order" not in code
        assert "strategy.close" not in code
