from src.bugbash import Scenario,run_scenario

def test_adversarial_inputs_block():
    cases=[Scenario("api_down",{"api_available":False},True),Scenario("future_leak",{"future_leakage":True},True),Scenario("duplicate",{"duplicate_candle":True},True),Scenario("stale",{"stale_data":True},True)]
    assert all(run_scenario(c).passed for c in cases)
def test_clean_case_allowed(): assert run_scenario(Scenario("clean",{},False)).passed
