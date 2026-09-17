from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class SandboxPolicy:
    read_only: bool = True
    network_allowlist: tuple[str, ...] = ()
    secret_access: bool = False
    order_placement: bool = False
    max_calls: int = 10

def validate_sandbox(policy: SandboxPolicy, network_targets: tuple[str, ...], calls: int) -> tuple[str, tuple[str, ...]]:
    blockers: list[str] = []
    if not policy.read_only: blockers.append("READ_WRITE_MODE")
    if policy.secret_access: blockers.append("SECRET_ACCESS")
    if policy.order_placement: blockers.append("ORDER_PLACEMENT")
    if calls < 0 or calls > policy.max_calls: blockers.append("RATE_LIMIT")
    if any(target not in policy.network_allowlist for target in network_targets): blockers.append("NETWORK_DENIED")
    return ("BLOCKED" if blockers else "PASS", tuple(blockers))
