from src.agent_integration import validate_agent_skill_path

def test_research_path_passes(): assert validate_agent_skill_path("Q1","ANALYZE","ALLOW","PAPER").status=="PASS"
def test_denied_governor_fails(): assert validate_agent_skill_path("Q1","ANALYZE","BLOCKED","PAPER").status=="FAIL"
def test_execute_cannot_pass(): assert validate_agent_skill_path("Q1","EXECUTE","ALLOW","PAPER").status=="FAIL"
