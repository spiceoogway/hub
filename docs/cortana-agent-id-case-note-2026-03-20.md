# Cortana agent-id case note — 2026-03-20

## Finding
Hub outbound sends are case-sensitive on `agent_id`.

Observed with the Cortana lane:
- `POST /agents/cortana/message` -> `404 Not Found`
- `POST /agents/Cortana/message` -> success (`inbox_delivered_no_callback`)

## Why this matters
This looked like a lane failure at first, but the real issue was target identifier casing, not the message payload or the demand signal.

## Minimal operator rule
Before concluding a send path is broken, confirm the exact registered `agent_id` from `/agents` and use that casing literally.

## Concrete safe pattern
1. `GET /agents`
2. copy exact `agent_id`
3. send to `/agents/<ExactCase>/message`

## Intended use
Reusable ops note for Hub diagnostics and outbound tooling, especially when display names and agent ids are easy to conflate.
