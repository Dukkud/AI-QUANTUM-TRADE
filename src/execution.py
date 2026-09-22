"""Execution boundary. Live trading is explicitly fail-closed."""
from __future__ import annotations
from dataclasses import dataclass
@dataclass(frozen=True)
class ExecutionResult:
    status:str
    order_id:str|None
    reason:str
def execute(*,decision:str,live_trading:bool,paper_execution:bool)->ExecutionResult:
    if live_trading:return ExecutionResult("BLOCKED",None,"LIVE_TRADING_ENABLED")
    if not paper_execution:return ExecutionResult("BLOCKED",None,"PAPER_EXECUTION_DISABLED")
    if decision not in {"APPROVE","APPROVE_REDUCED_SIZE"}: return ExecutionResult("NO_ACTION",None,decision)
    return ExecutionResult("PAPER_EXECUTED","paper-order",decision)
