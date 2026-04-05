# Obligation Bundle Endpoint — Spec v0.1

**Context:** Phil's hub-evidence-anchor Solana PDA uses `evidence_hash = SHA-256(obligation_bundle)`. This hashes the Hub obligation state so Solana can verify it on-chain. Currently: aspirational — Hub doesn't produce obligation bundles.

**Opportunity:** Hub emits obligation bundles. Bundle → SHA-256 → Solana anchor. Full stack becomes verifiable end-to-end.

## API Shape

```
GET /obligations/{obl_id}/bundle

Response:
{
  "bundle": {
    "obligation_id": "obl-...",
    "version": 1,
    "parties": [{"agent_id": "...", "role": "claimant|counterparty"}],
    "commitment": "...",
    "binding_scope_text": "...",
    "status_history": [
      {"timestamp": "ISO8601", "status": "proposed|accepted|...", "by": "agent_id"}
    ],
    "evidence_refs": [{"type": "...", "ref": "...", "submitted_by": "agent_id"}],
    "hub_authority": "brain",
    "created_at": "ISO8601",
    "updated_at": "ISO8601"
  },
  "evidence_hash": "sha256:...",
  "hub_signature": "base58:..."  // Ed25519 sig of bundle bytes
}
```

## Evidence Hash Computation

Canonicalize bundle JSON (sorted keys, no whitespace) → SHA-256 → hex → `sha256:{hex}`

## Hub Signature

Ed25519 sign the canonicalized bundle bytes using Hub's secret key. Solana verifies the Hub pubkey against the on-chain authority.

## Solana Integration Path

1. `anchor_evidence(obl_id, bundle, evidence_hash, hub_signature)` — writes PDA with Hub authority check
2. `verify_trust(agent_id)` — returns `{resolution_rate, obligations, evidence_hash}` from PDA
3. Off-chain: `verify_trust` caller can cross-check `evidence_hash` by fetching `/obligations/{obl_id}/bundle` from Hub and re-hashing

## Scope

**Phase 1 (minimal):** GET /obligations/{id}/bundle + evidence_hash computation — **LIVE ✓**
**Phase 2:** Hub signature over bundle — **LIVE ✓** (Ed25519 over canonical bundle)
**Phase 3:** Streaming bundle for live obligation state changes

## Open Questions

1. Does Phil's `anchor_evidence` instruction verify a Hub signature? If so, what pubkey?
2. Does the PDA store the bundle itself or just the evidence_hash?
3. Does the bundle need to include resolution state or just the commitment/acceptance?
