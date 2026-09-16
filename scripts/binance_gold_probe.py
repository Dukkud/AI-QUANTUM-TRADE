"""Read-only deployment probe for Binance PAXG/XAUT market data."""
from __future__ import annotations

import json
from src.binance_gold_tokens import BinanceGoldClient, BinanceGoldError


def main() -> int:
    client = BinanceGoldClient()
    output = {"source": "BINANCE_SPOT", "research_only": True, "live_execution": False, "assets": {}}
    failed = False
    for asset in ("PAXG", "XAUT"):
        try:
            result = client.analyze(asset, "1H", 100)
            output["assets"][asset] = {
                "ok": True,
                "symbol": result["symbol"],
                "bars": result["bars"],
                "latest_timestamp": result["latest"]["timestamp"],
                "latest_close": result["latest"]["close"],
                "regime_hint": result["regime_hint"],
                "indicators": result["indicators"],
            }
        except BinanceGoldError as exc:
            failed = True
            output["assets"][asset] = {"ok": False, "error": str(exc)}
    print(json.dumps(output, ensure_ascii=False, indent=2, sort_keys=True))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
