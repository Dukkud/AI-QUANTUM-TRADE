from src.skill_recovery import recover

def test_healthy_skill_stays_active():
    assert recover('s',False).status=='ACTIVE'

def test_failed_skill_uses_fallback_without_stopping_trading():
    r=recover('s',True,'fallback')
    assert (r.status,r.fallback_skill)==('FALLBACK','fallback')
    assert 'NO_TRADING_STOP' in r.reason

def test_failed_skill_without_fallback_is_disabled_fail_closed():
    assert recover('s',True).status=='DISABLED'
