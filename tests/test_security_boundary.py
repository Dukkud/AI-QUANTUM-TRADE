from src.security_boundary import validate_boundary

def base():
    return dict(live_trading=False,paper_execution=True,adaptive_updates=False,api_key_in_env=True,secret_exposed=False)

def test_clean_shadow_configuration_passes():
    assert validate_boundary(**base()).status=="PASS"

def test_live_trading_is_blocked():
    assert "LIVE_TRADING_ENABLED" in validate_boundary(**{**base(),"live_trading":True}).blockers

def test_paper_execution_disabled_is_blocked():
    assert "PAPER_EXECUTION_DISABLED" in validate_boundary(**{**base(),"paper_execution":False}).blockers

def test_adaptive_updates_are_blocked():
    assert "ADAPTIVE_UPDATES_ENABLED" in validate_boundary(**{**base(),"adaptive_updates":True}).blockers

def test_non_environment_secret_is_blocked():
    assert "SECRET_NOT_ENVIRONMENT_ONLY" in validate_boundary(**{**base(),"api_key_in_env":False}).blockers

def test_secret_exposure_is_blocked():
    assert "SECRET_EXPOSURE" in validate_boundary(**{**base(),"secret_exposed":True}).blockers

def test_multiple_security_blockers_are_fail_closed():
    r=validate_boundary(live_trading=True,paper_execution=False,adaptive_updates=True,api_key_in_env=False,secret_exposed=True)
    assert r.status=="BLOCKED" and len(r.blockers)==5
