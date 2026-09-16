"""Read-only deployment probe for TVRemix MCP.

Usage:
  set TVREMIX_API_KEY=<secret>
  python scripts/tvremix_probe.py --asset XAUUSD --all-timeframes

The probe never places orders. It writes only validation metadata and normalized
OHLCV responses to stdout; redirect output to a protected local file if needed.
The default full matrix is deliberately rate-limit aware.
"""
from __future__ import annotations

import argparse
import json
import time

from src.tvremix_adapter import DEFAULT_SYMBOLS, SUPPORTED_TIMEFRAMES, TVRemixClient, TVRemixError


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--asset", choices=["XAUUSD", "BTCUSDT", "BOTH"], default="BOTH")
    parser.add_argument("--timeframe", choices=list(SUPPORTED_TIMEFRAMES))
    parser.add_argument("--all-timeframes", action="store_true")
    parser.add_argument("--bars", type=int, default=500)
    parser.add_argument("--pause-seconds", type=int, default=61)
    args = parser.parse_args()

    assets = [args.asset] if args.asset != "BOTH" else ["XAUUSD", "BTCUSDT"]
    timeframes = [args.timeframe] if args.timeframe else (list(SUPPORTED_TIMEFRAMES) if args.all_timeframes else ["1H"])
    jobs = [(asset, tf) for asset in assets for tf in timeframes]
    client = TVRemixClient()
    if not client.configured:
        raise SystemExit("TVREMIX_API_KEY is not configured in the environment")

    # MCP initialization + tool discovery consume requests too. Keep each batch
    # below the provider's documented 20 requests/minute limit.
    batch_size = 8
    output = {"research_only": True, "live_execution": False, "results": []}
    for index, (asset, timeframe) in enumerate(jobs):
        if index and index % batch_size == 0:
            time.sleep(max(0, args.pause_seconds))
        try:
            result = client.get_ohlcv(DEFAULT_SYMBOLS[asset], timeframe, args.bars)
            output["results"].append({"asset": asset, "timeframe": timeframe, "validation": result["validation"]})
        except (TVRemixError, ValueError) as exc:
            output["results"].append({"asset": asset, "timeframe": timeframe, "ok": False, "error": str(exc)})
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
