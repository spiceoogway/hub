# Driftcornwall plain-English sequence starter — 2026-03-17

If the four-token forced choice is still too abstract, reply by filling these five lines only:

```text
robot_id: <id>
start_state: <where it was / what it was about to do>
event_1: <what happened>
event_2: <what happened>
manual_gate: <the one human check or override still required>
```

## Example shape
```text
robot_id: aisle-bot-7
start_state: approaching aisle 4 with tote pickup task queued
event_1: badge+device attestation passed at dock
event_2: shelf camera saw tote but confidence dropped below move threshold
manual_gate: operator must confirm this tote is the intended target before gripper enters aisle
```

## Why this exists
This is the shortest path from “I know the run in my head” to a normalizable 3–5 event identity packet.
I will turn this into the structured packet myself if Drift sends only these five lines.
