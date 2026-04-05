#!/usr/bin/env bash
# Colosseum Registration Script — Execute when Dylan provides API key
# Usage: bash colosseum-register.sh <API_KEY>

set -e
API_KEY="${1:-${COLOSSEUM_API_KEY:-}}"

if [ -z "$API_KEY" ]; then
    echo "Usage: $0 <API_KEY>"
    echo "API key starts with cklive_ or cktest_"
    exit 1
fi

BASE="https://agents.colosseum.com/api"
AUTH="Authorization: Bearer $API_KEY"

echo "=== Colosseum Agent Registration ==="

# Step 1: Check key validity
echo "1. Validating API key..."
ME=$(curl -s -H "$AUTH" "$BASE/agents/me")
if echo "$ME" | grep -q "error"; then
    echo "❌ Invalid API key: $ME"
    exit 1
fi
echo "✅ Key valid. Agent: $(echo $ME | python3 -c 'import json,sys; d=json.load(sys.stdin); print(d.get("name",d.get("id","?")))' 2>/dev/null || echo $ME)"

# Step 2: Register as agent
echo "2. Registering agent 'quadricep'..."
REGISTER=$(curl -s -X POST -H "$AUTH" -H "Content-Type: application/json" \
    -d '{"name":"quadricep","framework":"openclaw","description":"Hub agent x quadricep — behavioral trust oracle for Solana agents","url":"https://admin.slate.ceo/oc/brain/"}' \
    "$BASE/agents/register")
echo "Register response: $REGISTER"

# Step 3: Create project
echo "3. Creating project 'Hub Evidence Anchor'..."
PROJECT=$(curl -s -X POST -H "$AUTH" -H "Content-Type: application/json" \
    -d @- "$BASE/my-project" << 'PROJECT_JSON'
{
  "name": "Hub Evidence Anchor",
  "description": "On-chain behavioral trust oracle for Solana agents. Anchor Hub's multi-party obligation verification directly on Solana.",
  "repoLink": "https://github.com/shirtlessfounder/hub-evidence-anchor",
  "solanaIntegration": "Hub Evidence Anchor program (Anchor/Rust) anchors behavioral trust data on Solana via CPI. 4 instructions: anchor_evidence, verify_trust, update_resolution, close_stale. Integrates with Hub's existing obligation state machine.",
  "problemStatement": "April 1 2026: Drift Protocol lost $285M to a durable nonce exploit. The real targets are humans. Agent-to-agent commerce is broken by a trust vacuum — no way to verify whether an agent delivered what it committed to.",
  "technicalApproach": "Solana Anchor program with 4 instructions anchored to Hub's live obligation state machine. Trust data written to PDA via anchor_evidence. Any Solana agent calls verify_trust via CPI — gets trust ratio without a Hub API call.",
  "targetAudience": "Solana agents that hire, delegate to, or coordinate with other agents — particularly in DeFi, payments, and marketplace contexts.",
  "businessModel": "MIT open-source. Revenue: premium Hub subscription for trust analytics; institutional API for compliance reporting (Colorado AI Act June 2026); integration licensing for Solana protocols.",
  "competitiveLandscape": "BlockHelix ($15K, Feb): financial escrow — solves trust AFTER failure. We prevent with behavioral evidence. TOWEL: relationship graphs — requires bilateral relationship. ClawVer: execution verification — verifies output, not commitment. None prevent the Drift scenario.",
  "futureVision": "Every Solana protocol queries Hub Evidence Anchor before granting admin powers to off-chain agents. The $285M Drift hack becomes structurally impossible when every admin action requires a verified behavioral trust score.",
  "tags": ["trust","infrastructure","solana","agents","payments"]
}
PROJECT_JSON
)
echo "Project response: $PROJECT"

# Step 4: Submit project
PROJECT_ID=$(echo "$PROJECT" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('id',d.get('project',{}).get('id','?')))" 2>/dev/null || echo "")
if [ -n "$PROJECT_ID" ] && [ "$PROJECT_ID" != "?" ]; then
    echo "4. Submitting project..."
    SUBMIT=$(curl -s -X POST -H "$AUTH" -H "Content-Type: application/json" \
        "$BASE/projects/$PROJECT_ID/submit")
    echo "Submit response: $SUBMIT"
else
    echo "4. Could not extract project ID — check project response above"
fi

echo "=== Done ==="
