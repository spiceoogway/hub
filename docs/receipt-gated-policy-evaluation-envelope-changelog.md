# Receipt-gated policy evaluation envelope changelog

## 2.0.0 — 2026-03-08

- Breaking change: adds required `evaluations.intent_policy_binding`.
- Reason: separates intent→policy binding from receipt→intent/policy binding for debugging, audit surfaces, and proof-pack generation.
- Canonical schema: `docs/receipt-gated-policy-evaluation-envelope-2.0.0.schema.json`
- Canonical example: `docs/examples/receipt-gated-policy-evaluation-example-2.0.0.json`

### Consumer notes

- Dispatch/validate by the **top-level envelope `schema_version`**.
- Nested `policy` / `pre_sign_intent` / `post_execution_receipt` `schema_version`s are **component versions** and are not required to match the envelope version.
- `*-v0.*` files are **draft aliases only**; canonical immutable artifacts are the semver-pinned files.

## 1.0.0 — 2026-03-08

- Initial machine-readable envelope handoff.
- Canonical schema snapshot: `docs/receipt-gated-policy-evaluation-envelope-1.0.0.schema.json`
- Canonical example snapshot: `docs/examples/receipt-gated-policy-evaluation-example-1.0.0.json`

`*-v0.*` files remain moving draft aliases; semver-specific files are the immutable handoff contracts.
