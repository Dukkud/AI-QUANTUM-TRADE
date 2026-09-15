import math
from src.agent_decision_layer import run_agent_council
from src.v33_candidate_gate import ExecutionModel, brier, candidate_gate, metrics, run_v33


def bars(n=120):
    out=[]; p=100.0
    for i in range(n):
        p += 0.2 if i%7 else -0.05
        out.append({"timestamp":i,"open":p-0.1,"high":p+0.5,"low":p-0.5,"close":p,"volume":100+i})
    return out


def test_all_q_agents_exist_and_fail_closed_when_evidence_missing():
    r=run_agent_council({"bars":bars(),"data_quality_ok":False,"live_requested":False})
    assert [a["agent"] for a in r["agents"]]==["Q1","Q2","Q3","Q4","Q5","Q6","Q7","Q8"]
    assert r["quantum_decision"]=="HOLD" and r["hard_veto"] is True and r["live_execution"] is False


def test_q4_requires_real_history_and_positive_ev():
    r=run_agent_council({"bars":bars(),"historical_r":[1,-1]*20,"predicted_probability":0.6,"cost_r_per_trade":0.05,"data_quality_ok":True,"live_requested":False})
    q4=next(x for x in r["agents"] if x["agent"]=="Q4")
    assert q4["status"]=="ACTIVE" and "ev_net" in q4["evidence"]


def test_q3_refuses_synthetic_order_flow():
    r=run_agent_council({"bars":bars(),"data_quality_ok":True,"live_requested":False})
    q3=next(x for x in r["agents"] if x["agent"]=="Q3")
    assert q3["status"]=="DATA_UNAVAILABLE" and q3["decision"]=="HOLD"


def test_q8_hard_veto_is_explicit_for_live_account():
    r=run_agent_council({"bars":bars(),"data_quality_ok":True,"account_ready":False,"emergency_stop":False,"live_requested":True})
    q8=next(x for x in r["agents"] if x["agent"]=="Q8")
    assert q8["decision"]=="VETO" and "ACCOUNT_NOT_READY" in q8["evidence"]["vetoes"]


def test_cost_model_is_additive():
    m=ExecutionModel(0.1,0.2,0.3,0.4)
    assert math.isclose(m.total_cost_r,1.0)
    assert math.isclose(metrics([2,-1,1],m)["net_expectancy_r"],-1/3,abs_tol=1e-12)


def test_brier_is_deterministic():
    assert math.isclose(brier([0.9,0.1],[1,0]),0.01)


def test_candidate_gate_holds_on_bad_oos():
    g=candidate_gate([-1,-1,-1],ExecutionModel(),min_trades=3,robustness=True,anti_overfit_pass=True)
    assert g.passed is False and g.status=="HOLD" and "NON_POSITIVE_NET_EXPECTANCY" in g.reasons


def test_v33_is_always_research_only():
    rows=[{"pnl_r":1.0,"regime":"TREND","agent":"Q1","oos":True,"window":i} for i in range(100)]
    r=run_v33(rows)
    assert r["version"]=="33.0.0" and r["research_only"] is True and r["live_execution"] is False


def test_anti_overfit_detects_future_data_flag():
    rows=[{"pnl_r":1,"regime":"A","agent":"Q1","window":i,"future_data_used":(i==0)} for i in range(100)]
    r=run_v33(rows)
    assert r["anti_overfit"]["leakage_flag"] is True and r["gate"]["status"]=="HOLD"


def test_agent_attribution_has_groups():
    rows=[{"pnl_r":1,"regime":"A","agent":"Q1","window":i} for i in range(100)]
    r=run_v33(rows)
    assert "Q1" in r["agent_attribution"]
