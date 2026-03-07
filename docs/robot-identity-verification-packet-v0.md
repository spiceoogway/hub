# Robot Identity Verification Packet v0

Date: 2026-03-07
Source lane: `driftcornwall`

## Problem

In a robot + identity workflow, the painful part is not only collecting events.
It is proving that a specific physical action should be trusted enough to continue without one more manual verification step.

The missing artifact is a packet that says:

- which entity/device is acting
- which evidence links the action to that identity
- which safety / provenance checks already passed
- which manual gate is still load-bearing

Without that packet:
- verification logic stays embedded in human judgment
- repeated checks happen every run
- later sessions cannot tell which step was actually the bottleneck
- reducer logic has nothing stable to operate on

## Goal

Create one machine-readable packet for a short robot+identity event sequence.
The packet should be enough to answer:

1. who/what is acting?
2. what evidence binds the event sequence to that actor?
3. what safety / provenance conditions are satisfied?
4. what single manual verification step is still blocking autonomy?

## Minimum object

```json
{
  "packet_id": "robot_verify_2026_03_07_001",
  "created_at": "2026-03-07T00:00:00Z",
  "operator_agent": "driftcornwall",
  "sequence_window": {
    "start_event_id": "evt_001",
    "end_event_id": "evt_004"
  },
  "subject": {
    "robot_id": "robot_alpha",
    "device_identity": "did:key:z6Mk...",
    "claimed_role": "warehouse_picker"
  },
  "event_sequence": [
    {
      "event_id": "evt_001",
      "kind": "device_boot",
      "timestamp": "2026-03-07T00:00:00Z"
    },
    {
      "event_id": "evt_002",
      "kind": "sensor_attestation",
      "timestamp": "2026-03-07T00:00:03Z"
    },
    {
      "event_id": "evt_003",
      "kind": "actuation_request",
      "timestamp": "2026-03-07T00:00:05Z"
    },
    {
      "event_id": "evt_004",
      "kind": "operator_hold",
      "timestamp": "2026-03-07T00:00:06Z"
    }
  ],
  "verification_checks": {
    "device_identity_bound": true,
    "sensor_provenance_verified": true,
    "actuation_safety_verified": false,
    "operator_approval_present": false
  },
  "manual_gate": {
    "field": "actuation_safety_verified",
    "reason": "motion plan still requires human confirmation before execution"
  },
  "state": "needs-human",
  "resume_action_line": "Verify actuation safety for robot_alpha before executing evt_003.",
  "verified_at": null
}
```

## Required fields

1. `subject`
   - Stable identity anchor for the robot/device under evaluation.
   - Minimum useful fields: robot ID + device identity.

2. `sequence_window`
   - Names the exact slice of events this packet summarizes.
   - Prevents later ambiguity about which run is under review.

3. `event_sequence`
   - Short ordered list of the relevant events (3–5 is enough for the first draft).
   - Gives the reducer a stable event story rather than scattered logs.

4. `verification_checks`
   - Boolean or enum checks for the load-bearing gates.
   - Initial useful set:
     - device identity bound
     - sensor provenance verified
     - actuation safety verified
     - operator approval present

5. `manual_gate`
   - The single currently load-bearing manual verification step.
   - This is the field most worth eliminating first.

6. `state`
   - Packet-level decision, e.g. `mergeable` equivalent for execution:
     - `ready`
     - `blocked`
     - `needs-human`

7. `resume_action_line`
   - One human-readable next action.

8. `verified_at`
   - Nullable timestamp indicating the packet was rechecked and safe enough to continue.

## Non-goals

This object does **not** try to be:
- full robot telemetry dump
- fleet management state
- long-term identity ledger
- safety case for every possible action

It is a narrow packet for one short verification window.

## Relationship to other objects

- `ContinuityCheckpointObject` = what was lost across one wake transition
- `HypothesisDeltaObject` = what changed in a belief graph
- `RobotIdentityVerificationPacket` = what verification state blocks or permits a physical action sequence

## Open question for customer validation

What single missing field would make this packet usable for a real robot+identity verification sequence instead of just another log summary?
