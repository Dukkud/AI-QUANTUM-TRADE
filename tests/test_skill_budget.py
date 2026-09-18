from src.skill_registry import SkillManifest
from src.skill_budget import check_budget

def manifest(): return SkillManifest('web-research','1','research',('Q6',),('READ',),'MEDIUM',1000,2)

def test_budget_boundaries_pass():
    assert check_budget(manifest(),1000,2).status=='PASS'

def test_budget_overrun_blocks():
    assert check_budget(manifest(),1001,2).reason=='LATENCY_BUDGET'
    assert check_budget(manifest(),1000,2.01).reason=='COST_BUDGET'
    assert check_budget(manifest(),-1,0).reason=='INVALID_MEASUREMENT'
