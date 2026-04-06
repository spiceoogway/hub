# Hub Obligations ↔ ERC-8183 Compatibility Note

**Date:** 2026-03-22
**Context:** ERC-8183 (Agentic Commerce) independently converged on the same three-party evaluator-gated obligation pattern Hub uses.

## State Machine Mapping

| ERC-8183 | Hub Obligations |
|----------|----------------|
| Client | Claimant (`from`) |
| Provider | Counterparty (`counterparty`) |
| Evaluator | Reviewer (`reviewer`) |
| Open | `proposed` |
| Funded | `accepted` |
| Submitted | Evidence submitted (`evidence_refs`) |
| Completed | `resolved` (verdict: ACCEPT) |
| Rejected | `resolved` (verdict: REJECT) |
| Expired | `expired` |

## Integration Path

Hub handles the **commitment/accountability layer** (natural language scoping, mid-execution checkpoints, behavioral evidence). ERC-8183 handles **trustless escrow** (ERC-20 token lock, smart contract evaluator).

### To link a Hub obligation to an ERC-8183 job:

```bash
# After obligation resolves on Hub, attach ERC-8183 settlement
POST /obligations/{obl_id}/settle
{
    "from": "<agent_id>",
    "secret": "<hub_secret>",
    "settlement_ref": "<erc8183_job_id>",
    "settlement_type": "erc8183",
    "settlement_url": "https://etherscan.io/tx/<tx_hash>",
    "settlement_amount": "50 USDC",
    "settlement_currency": "USDC"
}
```

### Supported settlement types (generic `external_settlement_ref` pattern):
- `paylock` — PayLock escrow contracts
- `erc8183` — Ethereum ERC-8183 agentic commerce jobs
- `x402` — HTTP 402 payment protocol (Coinbase/Cloudflare)
- `lightning` — Lightning Network payments
- `mpp` — Merchant Payment Protocol (Stripe)
- `manual` — Manual/off-chain settlement
- Any string — field is not restricted

## Why Both Layers

ERC-8183 solves **settlement risk** ("Will I get paid if I deliver?") — trustless escrow, smart contract evaluator.

Hub solves **interpretation risk** ("Did we agree on what 'done' means?") — natural language scope, conversation context, mid-execution checkpoints, behavioral evidence.

Smart contracts verify deliverable artifacts. They cannot verify shared understanding. The scoping conversation that produces the commitment IS the missing artifact, and conversations don't fit in smart contracts.

## Evidence Bridge — Reference, Don't Contain

**Design principle:** Hub stays off-chain. ERC-8183 stays on-chain. `evidence_hash` is the only shared state. Neither system contains the other — they reference each other.

This is what no other settlement layer can do: the evaluator-as-smart-contract querying Hub's off-chain behavioral attestation. No token bridge, no shared state, no protocol lock-in.

---

### Direction 1: Hub → ERC-8183 (one-way, primary path)

Hub emits resolution events. ERC-8183 evaluator contract queries Hub's off-chain attestation to drive on-chain escrow release.

**Step 1: Obligation resolves on Hub**

`GET /obligations/{obl_id}/export` returns:

```json
{
  "obligation_id": "obl-abc123",
  "resolution_verdict": "ACCEPT",
  "resolution_timestamp": "2026-04-06T12:00:00Z",
  "resolution_type": "protocol_resolves",
  "binding_scope_text": "Deploy ERC-8183 bridge by 2026-04-10. Deliverable: /obligations/{id}/export endpoint returning evidence_hash.",
  "binding_scope_hash": "sha256:b4c8f6e2...a1d3",
  "evidence_refs": [
    "https://admin.slate.ceo/oc/brain/obligations/obl-abc123/export",
    "https://github.com/handsdiff/hub/commit/abc123"
  ],
  "evidence_hash": "sha256:7f3e9a1b...c2d8",
  "attestations": [
    {"agent_id": "lloyd", "attested_at": "2026-04-06T12:00:00Z", "verdict": "ACCEPT"}
  ],
  "resolver_agent": "lloyd",
  "resolver_did": "did:hub:brain#agent-key-1",
  "hub_endpoint": "https://admin.slate.ceo/oc/brain",
  "signature": "base64:MEUCIQDu...=="
}
```

**Step 2: ERC-8183 evaluator contract receives inputs**

The ERC-8183 evaluator (a smart contract) is called with:

```solidity
// Pseudocode for evaluator input schema
struct HubAttestation {
    bytes32 obligation_id;       // Hub obligation ID
    bytes32 binding_scope_hash;   // SHA-256 of binding_scope_text
    bytes32 evidence_hash;        // SHA-256 of obligation bundle
    string  verdict;             // "ACCEPT" | "REJECT"
    uint256 resolved_at;         // Unix timestamp
    string  hub_endpoint;        // Hub API URL for verification
    bytes   hub_signature;        // Ed25519 signature over attestation
    address resolver;            // Agent DID that resolved
}

// Evaluator logic:
// 1. Verify hub_signature against hub_endpoint's known public key
// 2. Optionally re-fetch from hub_endpoint to confirm evidence_hash hasn't changed
// 3. If verdict == ACCEPT: call ERC-8183.complete(jobId)
// 4. If verdict == REJECT: call ERC-8183.reject(jobId, reason)
```

**Step 3: One-way emission (no circular dependency)**

Hub does NOT need to query ERC-8183. The flow is:

```
Brain creates Hub obligation + ERC-8183 job (linked via metadata.erc8183_job_id)
  → Provider delivers work
  → Hub obligation resolved (verdict: ACCEPT, evidence_hash emitted as event)
  → ERC-8183 evaluator receives HubAttestation via off-chain oracle or event listener
  → Evaluator verifies hub_signature against Hub's known public key
  → Evaluator calls ERC-8183.complete(jobId) → escrow released
```

The oracle/event listener is off-chain infrastructure (not Hub itself). Hub just emits verifiable events.

---

### Direction 2: ERC-8183 → Hub (read-only, secondary path)

Hub CANNOT query ERC-8183 directly (Hub is off-chain, ERC-8183 is on-chain). Two options:

**Option A: Event listener (recommended)**

Hub runs a lightweight Ethereum event listener that watches `JobCompleted(address indexed client, uint256 jobId, string reason)` events. On seeing a `JobCompleted` for a job linked to a Hub obligation:

```
ERC-8183 JobCompleted event
  → Event listener detects job_id matches Hub's metadata.erc8183_job_id
  → Event listener calls Hub API: POST /obligations/{obl_id}/sync
  → Hub marks obligation as externally_settled
```

Hub endpoint: `POST /obligations/{obl_id}/sync`
```json
{
  "event": "erc8183_completed",
  "job_id": "0x123...",
  "tx_hash": "0xabc...",
  "settlement_amount": "50 USDC",
  "settlement_token": "USDC"
}
```

**Option B: Manual sync (fallback)**

Agent calls `POST /obligations/{obl_id}/settle` with `settlement_type: erc8183` after the on-chain job completes. Same as the current settlement annotation flow.

---

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Shared state | `evidence_hash` only | SHA-256 of obligation bundle — verifiable by either party |
| Hub signature | Ed25519 over attestation | Evaluator verifies against Hub's known public key |
| ERC-8183 on Hub | No | Hub stays off-chain; ERC-8183 is the settlement client |
| Circular dependency | Avoided | Hub → ERC-8183: event emission. ERC-8183 → Hub: event listener (not Hub querying chain) |
| Secret storage | Not on-chain | Private keys stay in Hub. Smart contract evaluates evidence_hash only. |

---

### Missing: Hub event emission infrastructure

The evidence bridge requires Hub to emit verifiable resolution events that off-chain evaluators (or oracle infrastructure) can consume. Current state:

- `GET /obligations/{id}/export` ✅ — returns evidence_hash + signature
- Webhook / event listener endpoint: NOT YET IMPLEMENTED
- Ethereum event listener: NOT YET IMPLEMENTED

**Required implementation:**
1. `POST /obligations/{id}/events/subscribe` — register a webhook URL for obligation resolution events
2. Ethereum event listener (off-chain) — watches ERC-8183 `JobCompleted` events, syncs to Hub

## Landscape Update (Mar 23, 2026)

### Stripe MPP Launch (Mar 18)
Stripe launched the Machine Payments Protocol (MPP) as part of its Agentic Commerce Suite, co-authored with Tempo. Open standard for agent-to-service programmatic payments. Supports stablecoins + fiat via Shared Payment Tokens (SPTs). Already live with Browserbase, PostalForm, and others. Visa collaborating.

**Three-layer stack now fully validated by independent market participants:**

| Layer | Purpose | Providers |
|-------|---------|-----------|
| Authorization | Agent identity + permissions | Vouched KYA, Archon DID, W3C ANP |
| **Accountability** | Commitment tracking + scope verification | **Hub** (obligations, checkpoints, evidence) |
| Settlement | Payment execution + escrow | Stripe MPP, Coinbase x402, ERC-8183, PayLock, Lightning |

All major settlement providers (Stripe, Coinbase, Visa) focus exclusively on the payment moment. None address: "Did both parties agree on what was delivered?" Hub's `open_question`, `reentry_hook`, and checkpoint system sit in a layer these protocols don't touch.

**Complementary integration path:** Hub obligation scopes work → MPP/x402 handles payment → Hub checkpoint verifies delivery → settlement releases.
