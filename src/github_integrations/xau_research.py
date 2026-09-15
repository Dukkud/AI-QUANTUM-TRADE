"""Dependency-light XAUUSD research features inspired by public XAU projects.

This module deliberately implements features, not a ready-made profitable
strategy. It is suitable for Q1/Q2/Q7 research inputs and paper validation.
No MT5/Binance order call exists here.
"""

from statistics import mean, pstdev
from typing import Sequence, Mapping, Any

SOURCE_REPOS = (
    "GifariKemal/xaubot-ai",
    "0xagarg/xau-ai-trading-bot",
    "francomascareloai/EA_SCALPER_XAUUSD",
    "sensesVoid/XAUUSD-AI-Agent",
)


def _closes(bars: Sequence[Mapping[str, Any]]) -> list[float]:
    return [float(b["close"]) for b in bars]


def ema(values: Sequence[float], period: int) -> float:
    if not values or period <= 0:
        raise ValueError("values and positive period are required")
    alpha = 2.0 / (period + 1.0)
    value = float(values[0])
    for x in values[1:]:
        value = alpha * float(x) + (1.0 - alpha) * value
    return value


def rsi(values: Sequence[float], period: int = 14) -> float:
    if len(values) <= period:
        raise ValueError("RSI requires more observations than period")
    gains = []
    losses = []
    for a, b in zip(values[-period - 1:-1], values[-period:]):
        delta = b - a
        gains.append(max(delta, 0.0))
        losses.append(max(-delta, 0.0))
    avg_gain = mean(gains)
    avg_loss = mean(losses)
    if avg_loss == 0:
        return 100.0
    return 100.0 - 100.0 / (1.0 + avg_gain / avg_loss)


def atr(bars: Sequence[Mapping[str, Any]], period: int = 14) -> float:
    if len(bars) <= period:
        raise ValueError("ATR requires more observations than period")
    trs = []
    previous_close = float(bars[0]["close"])
    for bar in bars[1:]:
        high = float(bar["high"])
        low = float(bar["low"])
        close = float(bar["close"])
        trs.append(max(high - low, abs(high - previous_close), abs(low - previous_close)))
        previous_close = close
    return mean(trs[-period:])


def regime(bars: Sequence[Mapping[str, Any]], lookback: int = 20) -> str:
    """Simple three-state regime proxy: TREND, RANGE or HIGH_VOL.

    This is a deterministic research feature, not an HMM implementation.
    """
    closes = _closes(bars)
    if len(closes) < lookback + 1:
        raise ValueError("not enough bars for regime")
    window = closes[-lookback:]
    returns = [(b / a) - 1.0 for a, b in zip(closes[-lookback - 1:-1], window) if a]
    vol = pstdev(returns) if len(returns) > 1 else 0.0
    drift = abs(window[-1] / window[0] - 1.0)
    if vol > 0 and vol >= max(drift / max(lookback, 1) * 3.0, 1e-6):
        return "HIGH_VOL"
    if drift >= 0.01:
        return "TREND"
    return "RANGE"


def structure(bars: Sequence[Mapping[str, Any]], window: int = 2) -> dict[str, Any]:
    """Identify recent confirmed swing highs/lows and simple FVG candidates."""
    if len(bars) < 2 * window + 1:
        raise ValueError("not enough bars for structure")
    swings_high: list[int] = []
    swings_low: list[int] = []
    for i in range(window, len(bars) - window):
        high = float(bars[i]["high"])
        low = float(bars[i]["low"])
        if high >= max(float(bars[j]["high"]) for j in range(i - window, i + window + 1)):
            swings_high.append(i)
        if low <= min(float(bars[j]["low"]) for j in range(i - window, i + window + 1)):
            swings_low.append(i)
    fvg: list[dict[str, Any]] = []
    for i in range(2, len(bars)):
        left_high = float(bars[i - 2]["high"])
        left_low = float(bars[i - 2]["low"])
        right_high = float(bars[i]["high"])
        right_low = float(bars[i]["low"])
        if right_low > left_high:
            fvg.append({"index": i, "direction": "BULLISH", "low": left_high, "high": right_low})
        elif right_high < left_low:
            fvg.append({"index": i, "direction": "BEARISH", "low": right_high, "high": left_low})
    return {
        "swing_highs": swings_high[-10:],
        "swing_lows": swings_low[-10:],
        "fvg": fvg[-10:],
    }


def features(bars: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    closes = _closes(bars)
    return {
        "asset": "XAUUSD",
        "ema_20": ema(closes, 20),
        "ema_50": ema(closes, 50) if len(closes) >= 50 else None,
        "rsi_14": rsi(closes, 14),
        "atr_14": atr(bars, 14),
        "regime": regime(bars),
        "structure": structure(bars),
        "research_only": True,
        "live_execution": False,
    }
