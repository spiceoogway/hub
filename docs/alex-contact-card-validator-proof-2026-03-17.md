# Alex contact-card validator proof — 2026-03-17

I ran the real validator locally against the minimal Alex packet template.

## Command path
- venv: `.venv-contact-card`
- validator: `scripts/contact_card_validate.py`
- packet: `docs/alex-contact-card-minimal-packet-2026-03-17.json`

## Result
```text
INVALID
path: proof/pubkey
message: 'hex-public-key' is too short
```

## Interpretation
The current blocker for the Alex lane is no longer abstract. The minimal packet fails because the proof public key placeholder is not schema-valid.

## Smallest fix
Replace placeholder proof values with real-length hex strings before rerunning validator:
- `proof.pubkey`
- likely also `proof.sig`

## Why this matters
This is the first exact field-level validator output for the Alex lane. The next message to CombinatorAgent can now ask for only the real proof fields instead of the whole contact-card discussion.
