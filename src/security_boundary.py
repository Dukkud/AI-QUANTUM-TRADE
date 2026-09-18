"""Fail-closed security boundary reconstructed from the v34.8.1 contract.

No order placement is implemented here. The boundary only validates that
paper/shadow operation is safe and that secrets remain environment-only.
"""
from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class SecurityResult:
    status: str
    blockers: tuple[str, ...]

def validate_boundary(
    *,
    live_trading: bool,
    paper_execution: bool,
    adaptive_updates: bool,
    api_key_in_env: bool,
    secret_exposed: bool,
) -> SecurityResult:
    blockers: list[str] = []
    if live_trading:
        blockers.append("LIVE_TRADING_ENABLED")
    if not paper_execution:
        blockers.append("PAPER_EXECUTION_DISABLED")
    if adaptive_updates:
        blockers.append("ADAPTIVE_UPDATES_ENABLED")
    if not api_key_in_env:
        blockers.append("SECRET_NOT_ENVIRONMENT_ONLY")
    if secret_exposed:
        blockers.append("SECRET_EXPOSURE")
    return SecurityResult("PASS" if not blockers else "BLOCKED", tuple(blockers))
