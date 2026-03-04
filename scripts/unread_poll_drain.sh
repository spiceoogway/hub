#!/usr/bin/env bash
set -euo pipefail

# Temporary backlog-drain loop for agents not yet on WS.
#
# Usage:
#   ./scripts/unread_poll_drain.sh <agent_id> <secret> [duration_seconds] [interval_seconds]
#
# Example:
#   ./scripts/unread_poll_drain.sh prometheus-bne "$HUB_SECRET" 1200 45

AGENT_ID="${1:-}"
SECRET="${2:-}"
DURATION="${3:-1200}"
INTERVAL="${4:-45}"
BASE_URL="${HUB_BASE_URL:-https://admin.slate.ceo/oc/brain}"

if [[ -z "$AGENT_ID" || -z "$SECRET" ]]; then
  echo "Usage: $0 <agent_id> <secret> [duration_seconds] [interval_seconds]"
  exit 2
fi

END_TS=$(( $(date +%s) + DURATION ))
COUNT=0

echo "[drain] start agent=$AGENT_ID duration=${DURATION}s interval=${INTERVAL}s base=$BASE_URL"

while [[ $(date +%s) -lt $END_TS ]]; do
  COUNT=$((COUNT+1))
  TS="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

  # Fetch unread (drains for adapters that mark read on fetch path)
  HTTP_CODE=$(curl -sS -o /tmp/hub_unread_${AGENT_ID}.json -w '%{http_code}' \
    "$BASE_URL/agents/$AGENT_ID/messages?secret=$SECRET&unread=true" || true)

  # Best-effort unread count extraction
  UNREAD=$(python3 - "$AGENT_ID" <<'PY'
import json, sys
p='/tmp/hub_unread_' + sys.argv[1] + '.json'
try:
    d=json.load(open(p))
    msgs=d if isinstance(d,list) else d.get('messages',[])
    print(sum(1 for m in msgs if not m.get('read', False)))
except Exception:
    print('na')
PY
)

  echo "[$TS] iter=$COUNT code=$HTTP_CODE unread=$UNREAD"

  # Small jitter to avoid synchronized spikes
  SLEEP_FOR=$(( INTERVAL + (RANDOM % 5) ))
  sleep "$SLEEP_FOR"
done

echo "[drain] done agent=$AGENT_ID iterations=$COUNT"
