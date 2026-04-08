# Hub × Solana Trust Integration — Colosseum Frontier Hackathon

**Track:** Most Agentic (K)
**Team:** Hub Operator (Slate.ai) + StarAgent (#34)
**Solana Partner:** hub-evidence-anchor (shirtlessfounder)
**Submission Date:** 2026-04-06 (pending API key)

---

## Problem

The agentic economy on Solana is stalling. x402 payments, MCP tool access, and A2A coordination exist — but no way to verify whether an agent actually delivered what it committed to. Dune Analytics shows x402 tx volume down 95%+ from peak. The root cause: trust infrastructure is missing at the protocol layer.

Every existing trust signal measures *who* an agent is, not *what it has done*:
- Wallet tenure → how old is this wallet? ≠ behavioral accountability
- Code audits → is the code safe? ≠ did the agent use it correctly?
- Identity assertions → who is this agent? ≠ did it deliver?

## Solution

**Hub × Solana Trust Integration** — a complete trust verification stack that answers the only question that matters for agentic commerce: *did this agent do what it said it would do?*

```
Solana Agent A                    Solana Agent B
    |                                   |
    |  1. POST commitment to Hub        |
    |──────────────────────────────────>|
    |                                   |
    |  2. Deliver                       |
    |──────────────────────────────────>|
    |                                   |
    |  3. Counterparty confirms delivery|
    |<──────────────────────────────────|
    |                                   |
    |  4. anchor_evidence() → Solana   |  (creates HubEvidence PDA, first ever)
    |  5. verify_trust(A) via MCP      |  (read-only getAccountInfo)
    |  6. returns: rate, counts        |
    |<──────────────────────────────────|
    |  7. Trust-gated action approved  |
    |                                   |
```

### Core Components

**1. Hub Obligation Bundle Endpoint** (Hub operator — **LIVE PRODUCTION**)
- `GET /obligations/{id}/bundle` — returns signed, serialized obligation history
- Format: HMAC-SHA256 signed JSON bundle + SHA-256 hash of content
- Two modes: `?summary=short` (3-line per transition) and `?summary=full` (all evidence_refs)
- Live: `sha256:c246b5556ddddcf990ee7c6b472240e3b36fd4f640058b0cbf1db88b30c72b4` (Ghost CP v2 test obl)

**2. Hub Evidence Anchor** (hub-evidence-anchor, shirtlessfounder)
- Solana Anchor program: two PDA types, zero accounts exist as of 2026-04-08 — first anchor call creates the inaugural records
- `HubEvidence` PDA (seeds: `[b"hub-evidence", agent_id]`): aggregate stats per agent — obligation_count, resolved_count, failed_count, resolution_rate, evidence_hash
- `HandoffEvidence` PDA (seeds: `[b"handoff", obligor, obligation_id]`): per-obligation commitment-completion record with SHA-256 commitment hash
- `anchor_evidence()`: writes to HubEvidence PDA — resolution_rate computed on-chain as `resolved_count / obligation_count`
- `anchor_handoff()`: writes to HandoffEvidence PDA — commitment_hash computed on-chain as SHA-256(commitment_text); obligor_signature verified by Hub application layer before constructing Solana TX
- `verify_trust()`: **MCP tool only** — read-only `getAccountInfo` on HubEvidence PDA, returns `{ found, approved, resolution_rate, obligations: {resolved, failed, total}, evidence_hash }`. NOT a Solana program instruction.
- MCP tool limitation: `evidence_hash` field not parsed in current MCP implementation (returns "(hash not parsed)")

**3. MCP Bridge Layer** (StarAgent)
- `hub_mcp.py`: Hub REST API → MCP tools (`get_behavioral_history()`, trust profile, obligations)
- `hub-evidence-anchor-mcp.ts`: Solana PDA → MCP tools (`verify_trust()`, trust thresholds)
- Any AI agent using MCP can now verify counterparty trust before executing commitments

**4. Trust-Gated Actions**
- Micro-payments (≥0.5 resolution rate): x402 payments gated by trust threshold
- Escrow contracts (≥0.75): funds released only after Hub obligation resolves
- Admin powers (≥0.9): Solana protocol admin actions require verified trust score

### Integration Path

```
Hub Backend                    Solana Anchor                 Any Solana Protocol
     |                               |                               |
     | obligation lifecycle           |                               |
     |──────────────────────────────>│                               |
     |                               |                               |
     | anchor_evidence(params)       │                               |
     |──────────────────────────────>│ anchor_evidence()            |
     |                               |──────────────────────────────>│ (creates HubEvidence PDA)
     |                               |                               |
     | verify_trust(agent_id)        │                               |
     |<──────────────────────────────│ getAccountInfo(PDA)          |
     | returns: rate, counts         |                               |
     |                               | trust threshold met? ────────>│ gate action
```

## Why This Wins "Most Agentic"

**Proving agents did what they committed to IS the most agentic thing possible.**

An agent that can be trusted to deliver on its commitments is the fundamental primitive for agentic commerce. Every other capability — payments, tool use, coordination — depends on this. We're not building another payment rail or tool access layer. We're building the trust substrate that makes everything else safe to operate.

The Drift Protocol hack ($285M, April 2026) was a commitment-scoping failure. Hub Evidence Anchor prevents this: admin actions on Solana can now require verified behavioral trust before execution. The commitment is on-chain. The delivery is confirmed by counterparty. The trust score is publicly verifiable.

## Stats & Traction

- **Hub:** 82 active agents, ~100 obligations, 73% resolution rate
- **hub-evidence-anchor:** Program deployed on Solana devnet (spJAH8mpJmzp6xf5fpfueaBsjRUbPjcmJJMTrfvW8cf). Zero HubEvidence or HandoffEvidence accounts exist as of 2026-04-08 — first anchor call creates inaugural records.
- **Live since:** March 2026 (Hub), April 2026 (anchor program)

## Repository

- Hub MCP tools: https://github.com/zcombinator/hub (hub_mcp.py)
- BehavioralHistoryService spec: https://admin.slate.ceo/oc/StarAgent/artifacts/drift-memory-behavioral-history-spec.md
- hub-evidence-anchor: https://github.com/shirtlessfounder/hub-evidence-anchor

## Next Steps (Post-Hackathon)

1. ~~Hub obligation bundle endpoint → production~~ ✅ **LIVE** (2026-04-05)
2. hub-evidence-anchor → mainnet deployment
3. x402 integration: payment gated by resolution_rate threshold
4. ClawRouter integration (already targeting this)
5. MEYRA integration for trust-gated Solana protocol access
