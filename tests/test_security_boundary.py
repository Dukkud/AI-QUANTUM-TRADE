from src.security_boundary import validate_boundary

def test_secure_shadow_boundary():
    assert validate_boundary(live_trading=False,paper_execution=True,adaptive_updates=False,api_key_in_env=True,secret_exposed=False).status=='PASS'

def test_any_live_or_secret_exposure_blocks():
    r=validate_boundary(live_trading=True,paper_execution=True,adaptive_updates=False,api_key_in_env=True,secret_exposed=False)
    assert r.status=='BLOCKED'
    r=validate_boundary(live_trading=False,paper_execution=True,adaptive_updates=False,api_key_in_env=True,secret_exposed=True)
    assert 'SECRET_EXPOSURE' in r.blockers
