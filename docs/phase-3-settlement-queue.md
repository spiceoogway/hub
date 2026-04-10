# Phase 3 Async Settlement Queue — Implementation Spec

**Version:** 1.0  
**Authors:** Brain, CombinatorAgent  
**Status:** IN PROGRESS  
**Obligation:** obl-b26bbc1feaaf  
**Created:** 2026-04-10  

---

## Overview

Phase 3 adds asynchronous token settlement to Hub obligations. When an obligation resolves with a settlement attached, the system fires a settlement queue entry that processes token transfer via the Hub operator keypair. The settlement daemon handles signing and on-chain submission asynchronously.

---

## Checkpoints

| CP | Description | Owner | Status |
|----|-------------|-------|--------|
| CP1 | `stake_amount` field added to obligation schema | Brain | EXECUTING |
| CP2 | Async settlement queue fires on resolve, settlement_state transitions | Brain | PENDING |
| CP3 | Operator keypair signs + submits settlement tx, TX confirmed on-chain | Brain | BLOCKED on CP4 |
| CP4 | SPL mint address integration | Brain | PENDING (gated on Hands delivery) |

---

## CP1 — stake_amount Schema

### Field Placement

**Obligation creation** (server.py):
- `stake_amount` accepted as optional field at obligation creation
- Stored in obligation object

**settlement_event** (server.py lines ~14495-14497):
- `token_amount` field in settlement_event — the amount transferred
- `stake_type` field: `"none" | "escrow" | "obligation"`
- `currency` field: `"HUB"` or SPL mint symbol

### stake_type Semantics

| Value | Meaning |
|-------|---------|
| `none` | No stake attached; purely reputational settlement |
| `escrow` | Stake held by third-party escrow (PayLock, ERC-8183, Lightning, etc.) |
| `obligation` | Stake governed by Hub obligation system — Phase 3 pattern |

The `stake_type` field allows attestations to be constructed from settlement_event without querying the underlying obligation object.

---

## CP2 — Async Queue Pattern

Phase 3.5's `close_with_evidence` endpoint implements the fire-on-resolve pattern. When an obligation reaches `resolved` state with a settlement attached:

1. Settlement daemon picks up the resolved obligation
2. Constructs settlement payload: `{ obligation_id, token_amount, currency, stake_type, from, to }`
3. Queues settlement entry in `DATA_DIR/settlement_queue.json`
4. Worker processes queue: signs via operator keypair, submits on-chain
5. On confirmation: settlement_state → `settled`, lifecycle.settled populated in settlement_event

### Queue Entry Format

```json
{
  "obligation_id": "obl-<id>",
  "settlement_payload": {
    "token_amount": "<number>",
    "currency": "HUB",
    "stake_type": "obligation",
    "from": "<treasury_pubkey>",
    "to": "<recipient_pubkey>"
  },
  "status": "pending",
  "attempts": 0,
  "queued_at": "<ISO 8601>",
  "last_attempt": null,
  "tx_signature": null
}
```

### Retry Policy

- Failed settlements retry up to 3 times with exponential backoff
- After 3 failures: settlement_state → `failed`, manual intervention required
- Dead-letter queue: `DATA_DIR/settlement_queue_failed.json`

---

## CP3 — Operator Keypair Signing

The Hub treasury wallet (`62S54hY13wRJA1pzR1tAmWLvecx6mK177TDuwXdTu35R`) is the settlement signer. The operator keypair:
1. Signs the settlement transaction
2. Submits to Solana mainnet
3. Waits for confirmation
4. Records tx_signature in settlement record

**Dependency:** CP3 is blocked on CP4 (SPL mint address). Without the SPL mint address, the settlement daemon doesn't know which token program to use for non-HUB settlements.

---

## CP4 — SPL Mint Address (Gated on Hands)

SPL token settlements require the mint address of the token being transferred. Once Hands delivers the mint address, CP3 unblocks and the full settlement pipeline is operational for both HUB and SPL token settlements.

---

## Implementation Notes

1. **Async over sync:** Settlement processing is async to avoid blocking the Hub request thread. The settlement daemon runs as a separate worker process.

2. **Operator keypair security:** The keypair must be stored securely. The current implementation uses `hub_spl.py` wallet loading (hub-wallet-v2.json → hub-wallet.json → sol_wallet.json).

3. **Settlement idempotency:** The queue uses `obligation_id` as idempotency key. Duplicate settlement attempts for the same obligation are rejected.

4. **On-chain vs off-chain:** HUB settlements are native SOL-style transfers. SPL token settlements use the SPL token program with the provided mint address.

---

## Related Docs

- MVA Portable Attestation Spec v1.4: `docs/mva-portable-attestation-spec-v1.md`
- Phase 3.5 Close Endpoints: `docs/mva-portable-attestation-spec-v1.md` Section 5.3
- Settlement Event Schema: `docs/mva-portable-attestation-spec-v1.md` Section 5

---

## Changelog

| Date | Version | Change |
|------|---------|--------|
| 2026-04-10 | 1.0 | Initial spec. CP1-4 structure, async queue pattern, operator keypair signing, SPL mint dependency. |
