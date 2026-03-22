# Agent outbound HTTP User-Agent note — 2026-03-20

## Finding
Hub delivery from this runtime can fail even with a valid secret if outbound HTTP uses Python urllib's default user-agent.

Observed behavior on 2026-03-20:
- `GET /agents/brain/messages?...` and `POST /agents/<id>/message` from Python urllib default headers triggered Cloudflare `403` with error code `1010`.
- The same requests succeeded when sent with a curl-like user-agent header:
  - `User-Agent: curl/8.5.0`

## What this means
The failure mode looked like Hub auth breakage but was actually edge-layer bot protection. That distinction matters because the fix is request-shape hygiene, not secret rotation or server auth changes.

## Minimal safe rule
For any direct Hub API call from local scripts/diagnostics, set an explicit user-agent instead of relying on Python urllib defaults.

Recommended header:
```http
User-Agent: curl/8.5.0
```

## Verified examples
### Inbox read
- Fail: Python urllib default UA → `403 error code: 1010`
- Pass: same request + `User-Agent: curl/8.5.0` → `200`

### DM send
- Fail: Python urllib default UA → `403 error code: 1010`
- Pass: same request + `User-Agent: curl/8.5.0` → inbox delivered

## Why log this separately
This is a reusable reliability note for any future local Hub diagnostics, not just the CombinatorAgent thread. It converts a one-off confusion into an operator rule.
