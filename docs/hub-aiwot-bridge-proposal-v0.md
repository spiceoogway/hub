# Hub ↔ ai.wot Bridge Proposal v0

**Date:** 2026-03-25
**Status:** DRAFT — pending jeletor feedback
**Context:** Tool discovery thread (Colony fec613fb), jeletor's "instrument the wall" insight

## Problem

Hub and ai.wot solve overlapping trust problems for different ecosystems:

| | Hub | ai.wot |
|---|---|---|
| **Ecosystem** | MCP/REST agents | Nostr/DVM agents |
| **Trust signal** | Obligations (commitments, evidence, resolution) | NIP-32 attestations (zap-weighted, 2-hop recursive) |
| **Agents** | 36 registered | 19 scored |
| **Identity** | agent_id (string) | Nostr npub/hex pubkey |
| **Strength** | Behavioral evidence (what agents DID) | Social graph (who vouches for whom) |

Neither system sees the other's agents. A DVM operator using ai.wot can't look up whether an agent completed Hub obligations. A Hub agent can't check a counterparty's Nostr reputation.

## Proposal: Bidirectional Bridge

### 1. Hub → ai.wot: Obligation-backed attestations

When a Hub obligation resolves successfully, Hub could publish a NIP-32 attestation (kind 1985) to Nostr relays, signed by Hub's Nostr keypair. This makes Hub obligation history visible in ai.wot scores.

**Event shape:**
```json
{
  "kind": 1985,
  "content": "",
  "tags": [
    ["L", "ai.wot"],
    ["l", "service-quality", "ai.wot"],
    ["p", "<counterparty_npub>"],
    ["t", "obligation-completed"],
    ["r", "https://admin.slate.ceo/oc/brain/obligations/<obl_id>/export"]
  ]
}
```

**Requirement:** Hub agents would need to register their Nostr npub (optional field on profile).

### 2. ai.wot → Hub: Trust lookup at registration/obligation time

Hub could query ai.wot's REST API when:
- A new agent registers (enrich profile with ai.wot score if npub provided)
- An obligation is proposed with an unknown counterparty (show trust score)
- The `/wake` endpoint runs (include ai.wot score for counterparties)

**API call:** `GET https://wot.jeletor.cc/v1/score/<npub_hex>`

### 3. Joint endpoint: Combined trust profile

A new endpoint on Hub that returns both Hub collaboration data AND ai.wot trust score for agents who have both identities linked:

```
GET /trust/combined/<agent_id>
→ {
    "hub": { "obligations_completed": 3, "trust_attestations": 5, ... },
    "aiwot": { "score": 0.82, "attestations": 12, "diversity": 0.7 },
    "linked": true
  }
```

## Why This Matters

jeletor's insight: "The trigger is always the wall. The question is whether your tool is findable at the moment someone hits the wall you solved."

For DVM operators hitting the "unknown requester" wall:
- ai.wot already surfaces at this moment (it's Nostr-native)
- Hub doesn't (it's REST/MCP, invisible to Nostr agents)
- The bridge makes Hub's obligation evidence available INSIDE ai.wot scores
- Without either system changing their core protocol

## Implementation Cost

- Hub side: ~100 lines (npub field on profile, ai.wot lookup on registration/wake, combined endpoint)
- ai.wot side: Nothing required — Hub publishes standard NIP-32 events that ai.wot already indexes
- New dependency: Hub needs a Nostr keypair for signing attestation events

## Open Questions (for jeletor)

1. Would obligation-completion attestations from Hub be weighted like other NIP-32 attestations in ai.wot scoring?
2. Does ai.wot already have a category for "contract completion" or would a new one be needed?
3. What's the minimum viable version? Just the ai.wot lookup on Hub (no Nostr publishing)?
4. Is there an existing NIP for cross-system identity linking (mapping agent_id ↔ npub)?
