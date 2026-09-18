from src.skill_registry import SkillManifest, SkillRegistry
from src.skill_governor import SkillGovernor, SkillRequest

def reg():
    return SkillRegistry((SkillManifest("web-research","1","research",("Q6",),("READ",),"MEDIUM",1000,2),))

def test_authorized_read_is_allowed():
    r=SkillGovernor(reg()).authorize(SkillRequest("web-research","Q6","READ","XAUUSD","1H","TREND"))
    assert (r.status,r.reason)==("ALLOW","AUTHORIZED")

def test_unauthorized_unknown_and_execute_are_blocked():
    g=SkillGovernor(reg())
    assert g.authorize(SkillRequest("web-research","Q1","READ","XAUUSD","1H","TREND")).status=="BLOCKED"
    assert g.authorize(SkillRequest("missing","Q6","READ","XAUUSD","1H","TREND")).reason=="UNKNOWN_SKILL"
    assert g.authorize(SkillRequest("web-research","Q6","EXECUTE","XAUUSD","1H","TREND")).reason=="SKILL_EXECUTION_FORBIDDEN"
