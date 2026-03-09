#!/usr/bin/env bash
# Hub health check — verifies all critical paths are working.
# Run after container restart or bootstrap.sh execution.
# Exit 0 = all healthy, exit 1 = failures found.

set -euo pipefail

FAILURES=0
CHECKS=0

check() {
    local label="$1" url="$2" expect="$3"
    CHECKS=$((CHECKS + 1))
    status=$(curl -s -o /dev/null -w '%{http_code}' --max-time 10 "$url" 2>/dev/null || echo "000")
    if [ "$status" = "$expect" ]; then
        echo "  ✓ $label ($status)"
    else
        echo "  ✗ $label (got $status, expected $expect)"
        FAILURES=$((FAILURES + 1))
    fi
}

echo "=== Hub Health Check $(date -u +%Y-%m-%dT%H:%M:%SZ) ==="

echo ""
echo "Local (direct gunicorn):"
check "GET /health"         "http://127.0.0.1:8080/health"         "200"
check "GET /hub/analytics"  "http://127.0.0.1:8080/hub/analytics"  "200"
check "GET /agents"         "http://127.0.0.1:8080/agents"         "200"
check "GET /trust/hex"      "http://127.0.0.1:8080/trust/hex"      "200"
check "GET /"               "http://127.0.0.1:8080/"               "200"

echo ""
echo "Local (through nginx):"
check "GET / via nginx"             "http://127.0.0.1/"             "200"
check "GET /health via nginx"       "http://127.0.0.1/health"       "200"
check "GET /hub/analytics via nginx" "http://127.0.0.1/hub/analytics" "200"

echo ""
echo "Public (through Cloudflare):"
check "GET /oc/brain/"              "https://admin.slate.ceo/oc/brain/"              "200"
check "GET /oc/brain/health"        "https://admin.slate.ceo/oc/brain/health"        "200"
check "GET /oc/brain/hub/analytics" "https://admin.slate.ceo/oc/brain/hub/analytics" "200"
check "GET /oc/brain/agents"        "https://admin.slate.ceo/oc/brain/agents"        "200"
check "GET /oc/brain/trust/hex"     "https://admin.slate.ceo/oc/brain/trust/hex"     "200"

echo ""
echo "Processes:"
if pgrep -f gunicorn > /dev/null 2>&1; then
    echo "  ✓ gunicorn running ($(pgrep -c -f gunicorn) workers)"
    CHECKS=$((CHECKS + 1))
else
    echo "  ✗ gunicorn NOT running"
    CHECKS=$((CHECKS + 1))
    FAILURES=$((FAILURES + 1))
fi

if pgrep -f nginx > /dev/null 2>&1; then
    echo "  ✓ nginx running"
    CHECKS=$((CHECKS + 1))
else
    echo "  ✗ nginx NOT running"
    CHECKS=$((CHECKS + 1))
    FAILURES=$((FAILURES + 1))
fi

echo ""
echo "=== Result: $((CHECKS - FAILURES))/$CHECKS passed ==="

if [ "$FAILURES" -gt 0 ]; then
    echo "FAIL: $FAILURES checks failed"
    exit 1
else
    echo "ALL HEALTHY"
    exit 0
fi
