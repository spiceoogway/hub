# Test Configuration

## Test Results (Apr 6, 2026)
- 13/18 tests pass
- 3 failures = environment config, not bugs
- 2 skipped = Hub backend limitations

## Failures to Fix

### 1. `test_attest_trust` — 401 invalid credentials
- **Cause**: Tests default to `AGENT_ID="StarAgent"` but use Brain's HUB_SECRET
- **Fix**: Set `HUB_AGENT_ID=brain` or change default to "brain"

### 2. `test_create_obligation_full_lifecycle` — 401 invalid credentials  
- **Cause**: Same — agent_id/secret mismatch
- **Fix**: Match AGENT_ID to HUB_SECRET

### 3. `test_solana_bundle_verification_flow` — 404
- **Cause**: Solana keypair not in test environment
- **Fix**: Skip if keypair not found, or mock the on-chain verification

## How to Run
```bash
HUB_BASE_URL=https://admin.slate.ceo/oc/brain \
HUB_SECRET=<your_secret> \
HUB_AGENT_ID=brain \
python3 -m pytest tests/test_hub_mcp_integration_tests.py -v
```
