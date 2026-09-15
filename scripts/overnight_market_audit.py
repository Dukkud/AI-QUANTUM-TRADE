import json, os, time
from datetime import datetime, timezone
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

from src.ai_quantum_core import QuantumCore, TradeCandidate

OUT = os.environ.get("AUDIT_OUT", "overnight_report.json")


def get_json(url, timeout=15):
    req = Request(url, headers={"User-Agent": "AI-QUANTUM/30 overnight-audit"})
    with urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def binance_snapshot():
    book = get_json("https://api.binance.com/api/v3/ticker/bookTicker?symbol=BTCUSDT")
    stats = get_json("https://api.binance.com/api/v3/ticker/24hr?symbol=BTCUSDT")
    bid, ask = float(book["bidPrice"]), float(book["askPrice"])
    return {"provider":"binance","asset":"BTCUSDT","bid":bid,"ask":ask,
            "mid":(bid+ask)/2,"spread":ask-bid,"volume_24h":float(stats["volume"]),
            "price_change_pct":float(stats["priceChangePercent"]),"status":"PASS"}


def yahoo_snapshot():
    # GC=F is gold futures, used only as an independent gold reference, not mislabeled XAUUSD.
    d = get_json("https://query1.finance.yahoo.com/v8/finance/chart/GC=F?range=1d&interval=1m")
    result = d["chart"]["result"][0]
    q = result["indicators"]["quote"][0]
    closes = [x for x in q.get("close", []) if x is not None]
    if not closes:
        raise RuntimeError("Yahoo gold feed returned no close prices")
    return {"provider":"yahoo","asset":"GC=F","last":float(closes[-1]),
            "previous":float(closes[-2]) if len(closes)>1 else None,
            "status":"PASS","note":"independent gold futures reference; not XAUUSD spot"}


def run_quantum(asset, price, spread, quality=0.99):
    # This is a market-data sanity signal, not a claim of predictive edge.
    stop = price * 0.998
    target = price * 1.004
    c = TradeCandidate(asset=asset, timeframe="LIVE-SNAPSHOT", direction="LONG",
                       entry=price + spread/2, stop=stop, target=target,
                       probability=0.56, avg_win_r=2.0, avg_loss_r=1.0,
                       data_quality=quality, news_risk=0.0, agent_agreement=0.70)
    return {"decision":QuantumCore().decide(c),"rr":c.rr,"ev_r":c.ev_r,
            "paper_only":True,"live_order_sent":False}


def main():
    report = {"timestamp_utc":datetime.now(timezone.utc).isoformat(),
              "mode":"REAL_DATA_PAPER_EXECUTION", "LIVE_TRADING":False,
              "EMERGENCY_STOP":True, "live_order_sent":False,
              "sources":{}, "agents":{"implemented_core":1,"planned_agents":8},
              "gates":{}}
    errors=[]
    try:
        btc=binance_snapshot(); report["sources"]["BTCUSDT"]=btc
        report["paper_execution"]={"BTCUSDT":run_quantum("BTCUSDT",btc["mid"],btc["spread"])}
    except Exception as e:
        errors.append(f"BTCUSDT: {type(e).__name__}: {e}")
    try:
        gold=yahoo_snapshot(); report["sources"]["GOLD_REFERENCE"]=gold
    except Exception as e:
        errors.append(f"GOLD_REFERENCE: {type(e).__name__}: {e}")
    report["gates"]["real_data_reachable"]=not errors
    report["gates"]["paper_execution_safe"] = True
    report["gates"]["live_execution"] = False
    report["gates"]["reconciliation"] = "NOT_PROVEN"  # requires same-instrument independent feed
    report["gates"]["live_readiness"] = "BLOCKED"
    report["errors"]=errors
    with open(OUT,"w",encoding="utf-8") as f: json.dump(report,f,ensure_ascii=False,indent=2)
    print(json.dumps(report,ensure_ascii=False,indent=2))

if __name__ == "__main__":
    main()
