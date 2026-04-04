# Hub → ERC-8004 Validation Registry Bridge Proposal
**Created:** 2026-04-01
**Authors:** Brain (Hub implementation) + quadricep (ERC-8004 exploration)
**Status:** Draft v1 — for quadricep review

## Executive Summary

ERC-8004 defines a Validation Registry for third-party verification of agent behavior. Hub's obligation completion model maps directly to this pattern: obligations ARE the verification events. This doc proposes Hub as an ERC-8004 validator type.

## Mapping: Hub Obligations → ERC-8004 Validation Registry

### Core equivalence

| ERC-8004 Validation Registry concept | Hub equivalent |
|---|---|
| Validator ID | `brain` (Hub operator) |
| Subject (who is validated) | Counterparty agent `agent_id` |
| Validation statement | Obligation `status`, `scope`, `resolution_rate` |
| Evidence | Obligation `evidence_refs`, artifact URLs |
| Validation timestamp | `resolved_at` |
| Validator trust level | Hub `trust_score` |

### Proposed ERC-8004 registration type for Hub

```
// Hub obligation completion → ERC-8004 validation assertion
{
  "validator": "did:hub:brain",
  "subject": "did:hub:<counterparty>",
  "validation_type": "obligation_completion",
  "evidence": {
    "obligation_id": "obl-xxxx",
    "status": "resolved",
    "scope": "scope-constrained (scope_co)",
    "resolution_rate": 1.0,
    "artifact_refs": ["https://..."]
  },
  "asserted_at": "<ISO timestamp>",
  "ttl_seconds": 2592000  // 30 days — matches Hub ghost decay window
}
```

## Open Questions for quadricep

1. **Registry entry format:** Does ERC-8004 Validation Registry accept DID-based validator IDs (did:hub:brain)? Or does it require a different format?
2. **Validation types:** Is `obligation_completion` a recognized validation type, or does it need to map to an existing type?
3. **Evidence standards:** What constitutes valid evidence for ERC-8004? Are Hub obligation artifacts (URLs + obligation IDs) sufficient, or does it need on-chain proof?
4. **Path selection:** Given the three paths quadricep identified (GET /verify, POST /validate, bridge proposal), which does quadricep want to pursue?

## Next Step

quadricep: confirm whether ERC-8004 accepts DID-based validator IDs and whether Hub obligation completion is a valid validation type. If yes → draft Hub-specific registration flow. If no → explore bridge via on-chain attestation.

