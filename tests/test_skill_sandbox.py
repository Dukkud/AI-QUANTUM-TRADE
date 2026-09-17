from src.skill_sandbox import SandboxPolicy, validate_sandbox

def test_default_read_only_allowlisted_network_passes():
    assert validate_sandbox(SandboxPolicy(network_allowlist=('api.example',)),('api.example',),1)==('PASS',())

def test_secret_write_order_network_and_rate_violations_block():
    status, blockers=validate_sandbox(SandboxPolicy(read_only=False,secret_access=True,order_placement=True,network_allowlist=('ok',),max_calls=1),('bad',),2)
    assert status=='BLOCKED'
    assert {'READ_WRITE_MODE','SECRET_ACCESS','ORDER_PLACEMENT','NETWORK_DENIED','RATE_LIMIT'} <= set(blockers)
