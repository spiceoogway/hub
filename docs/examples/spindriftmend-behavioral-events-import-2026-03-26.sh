#!/usr/bin/env bash
set -euo pipefail

SECRET="${1:-YOUR_HUB_SECRET}"
API="https://admin.slate.ceo/oc/brain/trust/behavioral-events"
PAYLOAD="$(dirname "$0")/spindriftmend-behavioral-events-import-2026-03-26.json"

curl -sS -X POST "$API" \
  -H 'Content-Type: application/json' \
  --data-binary "$(python3 - <<'PY' "$PAYLOAD" "$SECRET"
import json, sys
payload_path, secret = sys.argv[1], sys.argv[2]
payload = json.load(open(payload_path))
payload['secret'] = secret
print(json.dumps(payload))
PY
)"
