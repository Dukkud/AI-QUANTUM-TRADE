from src.skill_contracts import contract_is_valid

BASE={"skill_id":"s1","version":"1","purpose":"research","allowed_agents":["Q1"],"allowed_actions":["READ","ANALYZE"],"risk_class":"LOW","max_latency_ms":100,"max_cost_units":1}

def test_valid_contract():
    assert contract_is_valid(BASE)

def test_execute_is_forbidden():
    bad={**BASE,"allowed_actions":["READ","EXECUTE"]}
    assert not contract_is_valid(bad)

def test_invalid_budget_is_blocked():
    bad={**BASE,"max_latency_ms":0}
    assert not contract_is_valid(bad)
