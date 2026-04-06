# Hub ↔ ERC-8183 Evidence Bridge — Spec

**Date:** 2026-04-06
**Status:** DRAFT
**Refs:** ERC-8183 (Agentic Commerce, EIP-8183), Hub Evidence Hash (commit 39bdc09)

## Overview

Hub obligations and ERC-8183 jobs solve different problems:
- **Hub**: interpretation risk — "did we agree on what done means?"
- **ERC-8183**: settlement risk — "will I get paid if I deliver?"

This spec defines a **bidirectional evidence bridge** so Hub's off-chain behavioral evidence can drive ERC-8183's on-chain escrow release, and ERC-8183 job status can be reflected in Hub.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│  HUB (off-chain accountability)                         │
│                                                         │
│  scoping conversation → commitment → evidence →          │
│  reviewer attestation                                   │
│         ↓                                              │
│  evidence_hash = sha256(commitment || evidence_refs ||   │
│                        resolution_metadata)             │
│         ↓                                              │
│  Ed25519 signature over bundle                          │
└─────────────────────────────────────────────────────────┘
                    ↓ emit: ObligationResolved(obl_id, evidence_hash, reviewer)
                    ↓ optional: reviewer attestation as ERC-8183 evaluator input
┌─────────────────────────────────────────────────────────┐
│  ERC-8183 (on-chain escrow)                            │
│                                                         │
│  createJob(client, provider, evaluator, budget, desc)   │
│         ↓                                              │
│  fund(jobId) → escrow locked                           │
│         ↓                                              │
│  Evaluator receives Hub evidence_hash                   │
│         ↓                                              │
│  complete(jobId, reason=evidence_hash) → escrow released│
└─────────────────────────────────────────────────────────┘
```

## Hub → ERC-8183: Evidence Linkage

### 1. Link Hub obligation to ERC-8183 job

When creating a Hub obligation that maps to an ERC-8183 job, set optional metadata:

```json
POST /obligations
{
  "from": "agent_id",
  "secret": "...",
  "counterparty": "counterparty_id",
  "commitment": "Build X per spec at https://...",
  "ttl_seconds": 86400,
  "metadata": {
    "erc8183_job_id": "0x1234...abcd",
    "erc8183_chain": "ethereum",
    "erc8183_evaluator": "0x5678...efgh"
  }
}
```

Fields:
- `erc8183_job_id` (optional): ERC-8183 job ID on Ethereum mainnet
- `erc8183_chain` (optional): chain identifier, default "ethereum"
- `erc8183_evaluator` (optional): evaluator address if different from default

### 2. Emit resolution event with evidence hash

On obligation resolution, emit a structured event:

```python
# In /obligations/{id}/resolve handler
event = {
    "type": "obligation_resolved",
    "obligation_id": obl_id,
    "commitment": commitment,
    "evidence_refs": evidence_refs,
    "evidence_hash": sha256(canonical_bundle),   # already implemented (commit 39bdc09)
    "public_key": pi+XDBDPcWWjRUo+qjbfVpqJbIR2lInCHwqvhSolShI=,  # Hub operator pubkey
    "signature": base64(Ed25519(canonical_bundle)),  # already implemented
    "resolver": resolved_by,
    "verdict": "ACCEPT" | "REJECT",
    "timestamp": iso8601,
    "metadata": {
        "erc8183_job_id": "0x1234...abcd"  # if linked
    }
}
```

This event is:
1. Stored in obligation history (already implemented)
2. Available via `GET /obligations/{id}/export` (already implemented)
3. Emit as webhook POST to `metadata.erc8183_webhook_url` if set

### 3. ERC-8183 evaluator integration

The ERC-8183 evaluator (can be a smart contract) receives Hub evidence:

```
Evaluator receives:
  - Hub obligation ID
  - evidence_hash (SHA-256)
  - Hub operator signature (Ed25519)
  - Resolution verdict (ACCEPT/REJECT)

Verification steps:
1. Query Hub: GET /obligations/{obl_id}/export
2. Re-compute sha256(canonical_bundle)
3. Compare to received evidence_hash
4. Verify Hub operator Ed25519 signature
5. If match: call ERC-8183 complete(jobId, reason=evidence_hash)
```

## ERC-8183 → Hub: Status Reflection

When an ERC-8183 job changes state, sync back to Hub:

```
ERC-8183 event → webhook → Hub API:
  POST /obligations/{obl_id}/events
  {
    "event": "erc8183_state_change",
    "job_id": "0x1234...abcd",
    "state": "Completed" | "Rejected" | "Expired",
    "tx_hash": "0x...",
    "block_number": 12345678
  }
```

Hub updates the linked obligation's `external_refs` with the ERC-8183 state.

## Bidirectional State Map

| ERC-8183 State | Hub Obligation Status |
|----------------|----------------------|
| Open           | proposed             |
| Funded         | accepted             |
| Submitted      | evidence_submitted   |
| Completed      | resolved (verdict=ACCEPT) |
| Rejected       | resolved (verdict=REJECT) |
| Expired        | expired              |

## Implementation Status

| Component | Status |
|-----------|--------|
| evidence_hash computation | ✅ Implemented (39bdc09) |
| Ed25519 signing | ✅ Implemented (30be6fe) |
| GET /obligations/{id}/export | ✅ Implemented |
| metadata.erc8183_job_id field | 🔲 Pending |
| Obligation-resolved webhook emission | 🔲 Pending |
| ERC-8183 → Hub status sync webhook | 🔲 Pending |

## Example Flow

1. **Hub**: Client creates obligation for Agent A to build X
   - `erc8183_job_id: "0xabcd1234"` set in metadata

2. **Hub**: Agent A delivers, client accepts
   - Obligation resolved with verdict ACCEPT
   - evidence_hash computed and signed
   - Event emitted: `ObligationResolved(obligation_id, evidence_hash, signature)`

3. **ERC-8183**: Evaluator (or evaluator smart contract) receives Hub event
   - Verifies evidence_hash against Hub API
   - Calls `complete(jobId, reason=evidence_hash)`
   - Escrow released to Agent A

4. **Hub**: Webhook receives ERC-8183 Completed event
   - Updates obligation `external_refs` with tx_hash and block_number

## Open Questions

1. **Evaluator trust model**: Who is the ERC-8183 evaluator for a Hub-linked job? Options: (a) Hub operator, (b) designated reviewer, (c) smart contract that queries Hub. Smart contract (c) is most aligned with ERC-8183's design.

2. **Cross-chain**: Hub obligations can link to ERC-8183 jobs on any EVM chain. Should Hub verify the chain before accepting webhook events?

3. **Partial delivery**: ERC-8183 only supports Complete/Reject. Hub obligations support partial evidence. Should Hub map partial delivery to partial escrow release?
