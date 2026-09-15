# v32.2 Test Matrix

| Test | Purpose | Status |
|---|---|---|
| valid dataset | accepts structurally valid bars | PASS |
| invalid OHLC | rejects malformed price relationships | PASS |
| duplicate timestamp | rejects duplicate observations | PASS |
| non-monotonic timestamp | rejects temporal inversion | PASS |
| gap detection | reports missing interval without filling | PASS |
| fingerprint | stable SHA-256 dataset identity | PASS |
| deterministic replay | identical input -> identical events | PASS |
| research-only boundary | replay cannot enable live execution | PASS |
| app health version | exposes 32.2.0 | CI PENDING |
| app replay endpoint | integrated replay boundary | CI PENDING |
