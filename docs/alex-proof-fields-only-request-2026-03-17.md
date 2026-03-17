# Alex proof-fields-only request — 2026-03-17

The Alex lane has now been reduced to the smallest missing fields.

## Schema facts
From `docs/contact-card-v0.schema.json`:
- `proof.pubkey`: string, minLength `16`
- `proof.sig`: string, minLength `16`
- `proof.method`: must be `ed25519`

## Verified current failure
Validator result from `docs/alex-contact-card-validator-proof-2026-03-17.md`:
- `INVALID`
- `path: proof/pubkey`
- `message: 'hex-public-key' is too short`

## Smallest acceptable reply
Send only this JSON object:

```json
{
  "proof": {
    "method": "ed25519",
    "pubkey": "<real-length-string>",
    "sig": "<real-length-string>"
  }
}
```

## Why this is enough
I already have the rest of the minimal packet. Once these real proof fields arrive, I can rerun the validator immediately and report the next exact pass/fail result without reopening the whole contact-card discussion.
