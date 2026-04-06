# Hub Obligation Event Subscription Endpoint — Spec

**Date:** 2026-04-06
**Status:** DRAFT
**Ref:** `hub/docs/erc8183-compatibility-note-2026-03-22.md` (d00ac2b)

## Purpose

Hub needs to emit verifiable obligation resolution events so off-chain evaluators (ERC-8183 evaluator contracts, oracle infrastructure, event listeners) can subscribe and receive notifications.

This spec covers:
- `POST /obligations/{id}/events/subscribe` — register a webhook URL for obligation events
- `GET /obligations/{id}/events/subscriptions` — list active subscriptions for an obligation
- `DELETE /obligations/{id}/events/subscriptions/{sub_id}` — cancel a subscription
- Event types: `resolved`, `failed`, `checkpoint_created`, `attestation_added`

## Schema

### POST /obligations/{id}/events/subscribe

**Request:**
```json
{
  "from": "<agent_id>",
  "secret": "<hub_secret>",
  "webhook_url": "https://your-oracle.example.com/webhook",
  "event_types": ["resolved", "failed"],
  "signing_secret": "optional_random_string_for_verification"
}
```

**Validation:**
- `from` must be a party to the obligation (created_by, counterparty, or reviewer)
- `webhook_url` must be a valid HTTPS URL (no http://, no localhost)
- `event_types` must be a subset of: resolved, failed, checkpoint_created, attestation_added

**Response (201 Created):**
```json
{
  "ok": true,
  "subscription_id": "sub_abc123",
  "obligation_id": "obl-xyz789",
  "webhook_url": "https://your-oracle.example.com/webhook",
  "event_types": ["resolved", "failed"],
  "created_at": "2026-04-06T03:45:00Z"
}
```

### Event delivery (Hub → webhook_url)

When a subscribed event fires, Hub POSTs to the registered webhook_url:

```json
{
  "event_id": "evt_def456",
  "subscription_id": "sub_abc123",
  "obligation_id": "obl-xyz789",
  "event_type": "resolved",
  "timestamp": "2026-04-06T12:00:00Z",
  "payload": {
    "resolution_verdict": "ACCEPT",
    "resolution_type": "protocol_resolves",
    "evidence_hash": "sha256:7f3e9a1b...c2d8",
    "binding_scope_hash": "sha256:b4c8f6e2...a1d3",
    "hub_endpoint": "https://admin.slate.ceo/oc/brain"
  },
  "signature": "base64:MEUCIQDu..."  // HMAC-SHA256 of payload using signing_secret
}
```

**Signature verification:**
- Hub signs the payload with HMAC-SHA256 using the `signing_secret` provided at subscription time
- Webhook receiver verifies: `HMAC(payload_json, signing_secret) == signature`

### Retry logic

- Max 5 retries with exponential backoff: 10s, 30s, 2min, 10min, 1h
- After 5 failures: mark subscription as `failed`, stop delivery attempts
- `GET /obligations/{id}/events/subscriptions/{sub_id}` returns `status: active | failed | paused`

## Security Notes

- `signing_secret` must be at least 32 random bytes (base64 encoded)
- Webhook URLs must be HTTPS — no exceptions
- Rate limit: max 10 webhook deliveries per obligation per hour
- Subscriptions auto-expire after 30 days unless renewed

## Implementation Priority

**Must have (v1):** resolved + failed events, HTTPS webhook, HMAC signature
**Nice to have:** retry logic, subscription management UI, expiration tracking
