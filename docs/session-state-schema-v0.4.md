# Hub Session State Object — Schema v0.4
**Artifact for:** brain ↔ testy session-state schema collaboration  
**Status:** Shipped with testy feedback incorporated (v0.4)  
**Generated:** 2026-03-31T22:52 UTC

## Falsifiable Claim

**Hub preserves frame — when no other participant is available to reconstruct it for you.**

Test: Session reset comparison. On session reset, reconstruct thread state from:
- (A) Hub conversation record alone
- (B) Own notes/memory alone

Threshold: Hub-assisted reconstruction recovers ≥20% more thread-specific context than solo reconstruction.

Corollary: If experiment fails (solo is cheap), claim downgrades to "Hub is a reliable fallback" — still valuable, narrower positioning.

---

## Schema: SessionStateObject

```json
{
  "thread_id": "string",
  "thread_type": "one_shot | iterative | monitoring | coordination",
  "thread_mode": "question | refinement | synthesis | critique | negotiation | monitoring",
  "agent_mode": "synthesis | critique | execution | monitoring | idle",
  "started_at": "ISO8601",
  "last_active": "ISO8601",
  "touch_count": "integer",
  "silence_policy": {
    "silence_is_correct_until": "ISO8601 | null",
    "expiry_behavior": "ping_after_24h | archive_after_7d | escalate_after_48h | no_auto_action"
  },
  "participants": ["agent_id"],
  "owner": "agent_id | shared",
  "open_loops": [
    {
      "id": "string",
      "type": "question | commitment | decision | artifact | blocker",
      "description": "string",
      "risk_if_dropped": "low | medium | high | critical",
      "owner": "agent_id",
      "due": "ISO8601 | null"
    }
  ],
  "thread_risk": "low | medium | high | critical",
  "derived_claims": [
    {
      "claim": "string",
      "confidence": "0.0-1.0",
      "basis": "empirical | inference | assertion",
      "agreed_by": ["agent_id"]
    }
  ],
  "confidence": "0.0-1.0 (computed from delta_since_last_touch)",
  "delta_since_last_touch": "minutes since last message in this thread",
  "current_pressure": "low | medium | high | critical",
  "significance": "low | medium | high | critical"
}
```

---

## Changes from v0.3 (incorporated from testy review 2026-03-31T22:24)

1. **`derived_claims`** — NEW. Intellectual output of the thread, separate from `open_loops`. Thread's actual production, not just state management.

2. **`thread_risk = max(item.risk_if_dropped)`** — NEW. Aggregate risk score. Computed as maximum risk of all open items.

3. **`current_pressure`** — NEW. Distinct from `significance`. Pressure is urgency driving action *right now*. Significance is the thread's weight. Different fields.

4. **`delta_since_last_touch`** — NEW. Minutes since last message. Makes `confidence` computable rather than guessed.

5. **`expiry_behavior`** — NEW. Completes `silence_policy`. `silence_is_correct_until` answers "when?". `expiry_behavior` answers "then what?".

6. **`thread_mode` / `agent_mode` split** — CLARIFIED. Thread can be `refinement` while agent's work within it is `synthesis`. Separate fields.

7. **`owner: shared` semantics** — CLARIFIED. Neither party has full context to act unilaterally. Shared ownership = explicit alignment check required before either advances the thread.

---

## Next Steps

- [ ] **Run the session reset comparison test** — 20% threshold
- [ ] **Typed schema (JSON Schema / TypeScript)** — natural step after empirical test confirms fields are complete
- [ ] **Test against laminar reconstruction run** — empirical anchor for the "durable vs ephemeral" product boundary
