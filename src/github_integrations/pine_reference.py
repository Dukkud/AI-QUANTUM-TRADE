"""Pine Script v6 knowledge/validation boundary.

Source: codenamedevan/pinescriptv6. The repository is treated as an external
reference corpus, not as executable trading logic. The local contract below
captures the routing surface needed by AI-QUANTUM agents without copying the
reference corpus into production runtime.
"""

from dataclasses import dataclass
from typing import Iterable

SOURCE_REPO = "codenamedevan/pinescriptv6"
SOURCE_LICENSE = "Apache-2.0"

ROUTES = {
    "execution_model": "execution_model.md",
    "timeframes": "timeframes.md",
    "errors": "common_errors.md",
    "technical_analysis": "functions/ta.md",
    "strategy": "functions/strategy.md",
    "request": "functions/request.md",
    "drawing": "functions/drawing.md",
    "collections": "functions/collections.md",
    "general": "functions/general.md",
}

# High-risk Pine concepts that deserve explicit review before a generated
# TradingView script is accepted into research/backtest pipelines.
REVIEW_TERMS = (
    "request.security",
    "request.footprint",
    "lookahead",
    "barstate",
    "strategy.entry",
    "strategy.exit",
    "calc_on_every_tick",
    "timeframe",
)

@dataclass(frozen=True)
class PineValidation:
    ok: bool
    errors: tuple[str, ...]
    warnings: tuple[str, ...]
    matched_review_terms: tuple[str, ...]


def validate_script(script: str) -> PineValidation:
    """Perform dependency-free safety checks on Pine text.

    This is intentionally conservative. It is not a Pine compiler and must
    never be presented as proof that TradingView will compile a script.
    """
    errors: list[str] = []
    warnings: list[str] = []
    text = script or ""
    if not text.strip():
        errors.append("empty_script")
    if "//@version=6" not in text:
        warnings.append("pine_v6_declaration_missing")
    if "strategy(" in text and "strategy.entry" not in text and "strategy.order" not in text:
        warnings.append("strategy_declared_without_order_call")
    matched = tuple(term for term in REVIEW_TERMS if term in text)
    if "request.security" in text and "lookahead" in text:
        warnings.append("review_mtf_lookahead_interaction")
    return PineValidation(not errors, tuple(errors), tuple(warnings), matched)


def route_topics(topics: Iterable[str]) -> list[str]:
    """Map agent questions to Pine reference sections."""
    result: list[str] = []
    for topic in topics:
        key = str(topic).strip().lower().replace(" ", "_")
        if key in ROUTES:
            result.append(ROUTES[key])
    return result
