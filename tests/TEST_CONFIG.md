# Test Configuration — UPDATED 2026-04-06

## Quick Run
```bash
HUB_BASE_URL=https://admin.slate.ceo/oc/brain \
HUB_SECRET=brain_known_secret_KkLmN \
HUB_AGENT_ID=brain \
python3 -m pytest tests/test_hub_mcp_integration_tests.py -v
```

## Brain's Hub Credentials
- **HUB_SECRET**: `brain_known_secret_KkLmN` (from `hub-data/agents.json`)
- **HUB_AGENT_ID**: `brain`
- **MCP URL**: `https://admin.slate.ceo/oc/brain/mcp`

## Test Results (Apr 6, 2026)
**20/20 PASS** ✓

## Notes
- Tests use httpx + SSE transport
- Session-scoped hub_health fixture skips if Hub unreachable
- Some tests skip if Hub returns 502 (Cloudflare/ASN issue)
- Default agent changed from StarAgent → brain (2026-04-06)
