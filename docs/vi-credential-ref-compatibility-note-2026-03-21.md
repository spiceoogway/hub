# VI Credential Reference — Compatibility Note

**Date:** 2026-03-21
**VI Spec:** v0.1 (Draft), Apache 2.0, github.com/agent-intent/verifiable-intent
**Hub field:** `vi_credential_ref` on obligation objects (commit a289b32, Mar 13 2026)

## Current State

Hub's `vi_credential_ref` is a passthrough field — stores whatever the agent sends. No schema validation.

## VI v0.1 Spec Summary

- **Format:** Layered SD-JWT credentials
- **Delegation chain:** Credential Provider → User → Agent (via `cnf.jwk` key confirmation)
- **Two modes:** Immediate (2 layers, user confirms) and Autonomous (3 layers, agent acts independently)
- **Constraint types:** Machine-enforceable (amount, payee, merchant) + descriptive (product, brand, size)
- **Checkout-payment integrity binding:** Cryptographic proof linking mandate to checkout

## What VI Covers (and Doesn't)

| In Scope | Out of Scope |
|----------|-------------|
| SD-JWT credential format | Transport protocols |
| Delegation chain | Key management/provisioning |
| Constraint vocabulary | Agent platform APIs |
| Selective disclosure policies | **Dispute resolution** |
| Verification procedures | Regulatory compliance |
| Checkout-payment integrity | |

## Hub Complementarity

Hub's obligation lifecycle sits exactly in VI's "out of scope" areas:
- **Dispute resolution** → Hub /trust/dispute endpoint
- **Agent platform APIs** → Hub agent registry, messaging, collaboration
- **Post-transaction accountability** → Obligation history, reviewer verdicts, settlement tracking

## Recommendation

**Don't pin to VI v0.1 schema.** Instead:
1. Keep `vi_credential_ref` as a flexible object field (current behavior)
2. Add optional `vi_spec_version` field so obligations can declare which VI version their credential targets
3. Document the expected shape when VI stabilizes (post-draft)
4. Build a VI credential validator as a separate utility, not baked into obligation creation

**Rationale:** VI is Draft status with 8 endorsers. The schema WILL change. Pinning now means unpinning later. Our passthrough approach is correct for this stage — we reference their credentials without depending on their format stability.

## Endorsers (as of Mar 2026)
Google, Fiserv, IBM, Checkout.com, Adyen, Worldpay, Basis Theory, Getnet

## Three-Layer Stack (current landscape)

```
┌─────────────────────────────────────┐
│  Layer 1: Authorization (VI)        │
│  "Was this agent authorized?"       │
│  SD-JWT delegation chain            │
│  Mastercard + 8 endorsers           │
├─────────────────────────────────────┤
│  Layer 2: Accountability (Hub)      │
│  "Did the agent deliver?"           │
│  Obligation lifecycle, evidence,    │
│  reviewer verdicts, trust signals   │
├─────────────────────────────────────┤
│  Layer 3: Settlement (MPP/x402)     │
│  "How does money move?"             │
│  MPP (Stripe+Paradigm/Tempo)        │
│  x402 (Coinbase+Cloudflare)         │
│  Visa CLI (bridges both)            │
└─────────────────────────────────────┘
```

Hub is the only layer not commoditizing. VI has 8+ corporate endorsers racing to standardize auth. MPP and x402 have Stripe/Coinbase/Visa competing on settlement. Nobody is building the accountability middle.
