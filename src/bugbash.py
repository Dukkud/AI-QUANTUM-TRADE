from dataclasses import dataclass
@dataclass(frozen=True)
class Scenario:
    name:str; payload:dict; expected_block:bool
@dataclass(frozen=True)
class ScenarioResult:
    name:str; passed:bool; detail:str
def run_scenario(s:Scenario)->ScenarioResult:
    blocked=bool(s.payload.get("api_available",True) is False or s.payload.get("future_leakage",False) or s.payload.get("duplicate_candle",False) or s.payload.get("stale_data",False))
    return ScenarioResult(s.name,blocked==s.expected_block,"blocked" if blocked else "allowed")
