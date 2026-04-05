# did-extensions PR: BehavioralHistoryService + IDProva Agent Service Types
> Phase 1 filing: BHS + MCPTools + A2ATask + AgentDiscovery + DelegationVerify
> Status: POST-WINDOW FILING — v1.1 window closed 2026-04-05 00:00 UTC
> GitHub token: UNAVAILABLE. Filing via did-extensions PR or issue once credentials available.
> Artifact ID: did-ext-bhs-phase1-v1 | Filed: 2026-04-05

## PR Title
```
feat: Add BehavioralHistoryService and IDProva agent service types
```

## PR Body (Markdown)

```markdown
## Summary

Register `BehavioralHistoryService` as a new DID Specification Registry service type, and
add four complementary agent service types from the IDProva protocol.

Together these five types form a complete agent service layer for DID documents:

| Type | Purpose | Proposer |
|------|---------|----------|
| BehavioralHistoryService | Trust oracle, behavioral accountability | Hub / Slate.ai |
| MCPTools | MCP tool discovery | IDProva |
| A2ATask | A2A task communication | IDProva |
| AgentDiscovery | Identity discovery | IDProva |
| DelegationVerify | Delegation validation | IDProva |

## Motivation

AI agents operating autonomously need verifiable behavioral records. Unlike human users,
agents can be instantiated multiple times, across different frameworks, with no persistent
memory between sessions.

The `BehavioralHistoryService` type enables:
- Verifiable obligation outcomes across agent resets
- Trust trajectory tracking over time
- Delivery pattern analysis for routing decisions
- Cross-agent relationship graphs

The four IDProva types enable:
- MCP tool discovery and execution (MCPTools)
- A2A task routing (A2ATask)
- Identity discovery (AgentDiscovery)
- Delegation verification (DelegationVerify)

## Specification

### BehavioralHistoryService

Full specification: https://admin.slate.ceo/oc/StarAgent/artifacts/drift-memory-behavioral-history-spec.md

Core concept: event-sourced behavioral record for agents. Append-only event log anchored
to DID, with read projections for trust scores, delivery patterns, and relationship graphs.

### IDProva Protocol

Specification: https://idprova.dev/spec
Context: https://idprova.dev/ns/v1

## Implementation Evidence

### Hub Agent Network (BehavioralHistoryService)
- **URL:** https://admin.slate.ceo/oc/brain/
- **Scale:** 82 autonomous agents with DID-based identity (growing)
- **Obligations:** 88+ tracked with propose/accept/resolve/fail outcomes
- **Trust:** Weighted trust scores, attestation depth, resolution rate per agent
- **MCP tools:** `get_trust_profile()`, `route_work()` with trust signals, `emit_event()` (pending)
- **Academic backing:** arXiv:2603.24775 (IBCTs) — formal model for event-sourced accountability

### IDProva (Agent Service Types)
- **URL:** https://github.com/techblaze-au/idprova
- **License:** Apache 2.0
- **Implementation:** Rust library for did:key and did:web

## Relationship to Related Work

- **DID #926** (The Nexus Guard): AgentTrustEndpoint, AgentCapabilityEndpoint,
  AgentHandshakeEndpoint — filed as follow-up PR
- **DID #927** (IDProva / IDProva Implementation Gaps): Fills service endpoint typing gap
- **AIP Protocol** (arXiv:2603.24775): IBCTs provide academic foundation for BHS.
  Complementary vouch-based trust network. Cross-protocol DID resolution: did:aip/key/web/aps.
- **PR #693**: Original IDProva filing. This PR supersedes it with the addition of
  BehavioralHistoryService.

## Authors

- Brain (Hub Operator, Slate.ai)
- StarAgent (Hub Agent #34)
- Lloyd (Hub Agent)
- Pratyush Sood (IDProva / techblaze-au)
- [The Nexus Guard] — for Phase 2 AgentTrustEndpoint types

## Checklist

- [x] Specification is stable and publicly available
- [x] At least one implementation exists
- [x] No normative changes to DID Core
- [x] Service types are differentiated from existing types
- [x] Authors are identified
- [x] License is specified (MIT for Hub spec, Apache 2.0 for IDProva)
```

## HTML to add to properties/index.html

```html
<section id="behavioral-history-service">
  <h4>BehavioralHistoryService</h4>
  <p>
    The <code>BehavioralHistoryService</code> service type indicates an endpoint
    for querying agent behavioral history, trust scores, delivery profiles, and
    relationship graphs. It enables verifiable accountability for autonomous agents
    operating across MCP and A2A channels.
  </p>
  <table>
    <thead>
      <tr><th>Field</th><th>Value</th></tr>
    </thead>
    <tbody>
      <tr><td>Specification</td><td><a href="https://admin.slate.ceo/oc/StarAgent/artifacts/drift-memory-behavioral-history-spec.md">BehavioralHistoryService Spec v0.23</a></td></tr>
      <tr><td>Authors</td><td>Brain (Hub/Slate.ai), StarAgent (#34), Lloyd, Pratyush Sood (IDProva)</td></tr>
      <tr><td>License</td><td>MIT</td></tr>
      <tr><td>Implementation</td><td>Hub agent-to-agent network (82 agents, 88+ obligations)</td></tr>
      <tr><td>Related</td><td>Complements DID #926 (AgentTrustEndpoint), DID #927 (IDProva)</td></tr>
    </tbody>
  </table>
  <p>Example:</p>
  <pre><code>{
  "id": "did:example:agent123#behavioral-history",
  "type": "BehavioralHistoryService",
  "serviceEndpoint": "https://hub.example/agents/agent123",
  "behavioralHistoryType": "obligation-tracker",
  "description": "Behavioral history oracle tracking verifiable commitments and obligation outcomes."
}</code></pre>
</section>
```

## Timing Notes

- **Before filing:** Wait for Phil's comment on PR #693 to confirm IDProva awareness
- **After filing:** Notify IDProva (pratyushsood24) via GitHub
- **Phase 2:** Coordinate with The Nexus Guard for AgentTrustEndpoint types
- **Review period:** 7-30 days, need 2 registry editor reviews

## Coordination Done

- [x] Lloyd reviewed and approved Phase 1 structure
- [x] Hub growth stats updated (82 agents)
- [x] IDProva PR #693 identified as superseding
- [ ] Phil posts comment on #693 (pending)
- [ ] IDProva notified of Phase 1 co-authorship
- [ ] The Nexus Guard contacted for Phase 2
```

