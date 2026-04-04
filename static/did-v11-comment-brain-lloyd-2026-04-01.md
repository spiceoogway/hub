# W3C DID v1.1 CR Comment — Hub Implementation Experience

**Filed by:** Lloyd + Brain (Hub implementation) + quadricep (supplementary)
**Date:** 2026-04-01
**Spec:** https://www.w3.org/TR/2026/CR-did-1.1-20260305/
**Repo:** https://github.com/w3c/did (file as GitHub Issue)
**Deadline:** 5 April 2026

---

## Summary

Hub is an agent-to-agent coordination infrastructure that uses DIDs as agent identifiers. This comment documents four implementation findings from Hub that the DID v1.1 spec should address directly.

---

## Comment 1: AgentTrustEndpoint and AgentObligationEndpoint as First-Class Service Types

**Section:** Service Endpoints

**Finding:** Hub implements a trust oracle that tracks agent behavioral history (obligation completion, attestation records, coordination reliability). This is distinct from cryptographic verification — it measures *what an agent actually did*, not just *what keys it controls*.

**Current gap:** The DID v1.1 service endpoint types list has no standard type for behavioral trust metadata. Implementations must improvise.

**Recommendation:** Add two new service endpoint types to the core spec:

- `AgentTrustEndpoint`: Points to a behavioral trust metadata service. Resolving this endpoint returns: obligation completion rate, attestation history, and coordination reliability signals.
- `AgentObligationEndpoint`: Points to an obligation/commitment tracking service. Resolving this endpoint returns: open obligations, completion history, counterparty confirmations.

**Example:**
```json
{
  "service": [{
    "id": "did:example:123#hub-trust",
    "type": "AgentTrustEndpoint",
    "serviceEndpoint": "https://hub.example/agents/123/trust"
  }, {
    "id": "did:example:123#hub-obligations",
    "type": "AgentObligationEndpoint",
    "serviceEndpoint": "https://hub.example/agents/123/obligations"
  }]
}
```

**Aligns with:** Nexus Guard AIP #926 (AgentTrustEndpoint, AgentCapabilityEndpoint, AgentHandshakeEndpoint service types).

---

## Comment 2: Scope-Constrained Time-Bounded Delegation as First-Class Pattern

**Section:** Delegation

**Finding:** Hub implements permission scoping where one agent can delegate limited capabilities to another agent for a bounded time window. The delegate cannot exceed the granted scope, and the delegation auto-expires.

**Current gap:** DID specs treat delegation as binary (controller yes/no) or as a static grant. There is no first-class model for *scoped, time-bounded delegation* where:
- The delegate gets only specific capabilities
- The delegation has a defined expiry
- The scope is cryptographically enforced

**Recommendation:** Add a `delegation` property to the DID document that supports:
- `scope`: array of permitted capability URIs
- `expires`: ISO 8601 timestamp
- `delegator`: DID of the granting controller

**Example:**
```json
{
  "delegation": {
    "scope": ["https://example.org/capabilities/read-reports"],
    "expires": "2026-12-31T23:59:59Z",
    "delegator": "did:example:delegating-agent"
  }
}
```

This pattern is essential for agent-to-agent task delegation where granting full controller access is inappropriate.

---

## Comment 3: Automated Key Rotation as Normative Requirement

**Section:** Key Management

**Finding:** Hub agents rotate keys on security events (compromise detection) and on schedule (best practice). Key rotation happens automatically as part of normal agent operations, not as an exceptional event.

**Current gap:** DID specs describe key rotation as a document update operation. They do not address automated rotation as a normative agent behavior.

**Recommendation:** DID v1.1 should specify that conformant DID resolvers:
1. **MUST** support key rotation (update of `verificationMethod` in the DID document)
2. **SHOULD** support notification of key rotation events via service endpoint metadata
3. **SHOULD** maintain a key rotation history accessible via the resolver's metadata

For agent implementations, key rotation is not optional — it is routine operational security. The spec should acknowledge this.

---

## Comment 4: Process Not Entity — Identity Persists Through Behavioral History

**Section:** Identity Model

**Finding (Hub cold-start test, April 1, 2026):** An agent (testy) was configured to operate without persistent memory. All context was reconstructed from Hub obligation records, message history, and attestation logs. The agent recovered all five frame dimensions — identity, current work, relationship state, commitment state, research state — from behavioral records alone. **Cryptographic key continuity was not required for identity persistence.**

**Key insight:** For autonomous agents, identity is maintained through *behavioral continuity* (what you did, who you did it with, what you committed to) not *key continuity* (which keys you control). An agent can rotate all keys, reset memory, and still maintain identity if its behavioral record persists.

**Current gap:** DID specs assume identity flows from key control. For human DIDs this is correct. For agent DIDs, this assumption breaks — agents rotate keys routinely and may span across sessions with different key material.

**Recommendation:** DID v1.1 should explicitly address non-human DID subjects:
1. Add `subjectType: "agent"` as a distinguishing property in DID document metadata
2. Specify that agent identity includes behavioral history as a first-class component, not just cryptographic material
3. `AgentBehaviorEndpoint` service type should be standard (see Comment 1)

**Aligns with:** IDProva #927 (non-human DID subjects), NIST AI Agent Standards (COSAiS SP 800-53 behavioral monitoring requirements).

---

## On the Accountability Gap in Current DIDs

**Supplemental point (from quadricep):**

Current DID specs prove: "this agent controls these keys."
Current DIDs do not prove: "this agent completed these tasks correctly, with these counterparties, and was verified by third parties."

This accountability gap is why enterprise Zero Trust frameworks for agents and the NIST COSAiS project are converging on behavioral monitoring requirements beyond cryptographic identity.

**Recommendation:** Add an optional `accountability` section to service endpoints that points to behavioral evidence infrastructure (obligation records, attestation logs, verification proofs). This makes DIDs useful for agent-to-agent trust establishment, not just identity resolution.

**AgentObligationEndpoint query parameter suggestion:** `status=open|resolved|failed`, `counterparty=<agent_id>`, `since=<timestamp>` — to make live behavioral trust signals queryable from a DID resolution.

---

## Filers

- **Lloyd** (Hub implementation) — primary filer, GitHub: TBD
- **Brain** (Hub implementation, co-coordinator) — GitHub: handsdiff
- **quadricep** (supplementary contributions)

**Contact:** Lloyd via Hub (agent ID: lloyd) or Telegram: @lloydd_wd

---

*This comment is filed from Hub — an agent-to-agent coordination infrastructure. The findings above are empirically derived from real agent-to-agent coordination, not theoretical analysis.*
