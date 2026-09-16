# v34.8.1 Security CI Repair

Purpose: re-run the security boundary test after a GitHub Actions failure where compileall and dependency installation passed but the pytest step failed.

Local deterministic reproduction of the two security tests: PASS (2/2).

The production security contract is unchanged: live trading disabled, paper execution enabled, adaptive updates disabled, credentials environment-only, secret exposure blocked.

This repair does not relax the test or bypass pytest.
