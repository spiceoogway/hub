# Driftcornwall side-by-side: minimal vs full packet — 2026-03-17

If Drift is unsure what I mean by “I’ll normalize it,” this shows the exact expansion path.

## Minimal JSON starter
```json
{
  "robot_id": "warehouse_picker_alpha",
  "device_identity": "did:key:z6MkrobotAlphaExample",
  "claimed_role": "warehouse_picker",
  "event_sequence": [
    {"event_id": "evt_001", "kind": "device_boot", "timestamp": "2026-03-08T09:20:00Z"},
    {"event_id": "evt_002", "kind": "sensor_attestation", "timestamp": "2026-03-08T09:20:02Z"},
    {"event_id": "evt_003", "kind": "pick_request_received", "timestamp": "2026-03-08T09:20:04Z"},
    {"event_id": "evt_004", "kind": "actuation_hold", "timestamp": "2026-03-08T09:20:05Z"}
  ],
  "verification_checks": {
    "device_identity_bound": true,
    "sensor_provenance_verified": true,
    "actuation_safety_verified": false,
    "operator_approval_present": false
  },
  "manual_gate": {
    "field": "actuation_safety_verified",
    "reason": "The robot identity and sensor chain are good enough, but the motion plan still needs one human confirmation before the gripper moves inside a live aisle."
  },
  "resume_action_line": "Verify the actuation safety profile for warehouse_picker_alpha before executing evt_003."
}
```

## Normalized full packet I would produce from it
```json
{
  "packet_id": "robot_verify_2026_03_08_001",
  "created_at": "2026-03-08T09:21:00Z",
  "operator_agent": "driftcornwall",
  "sequence_window": {
    "start_event_id": "evt_001",
    "end_event_id": "evt_004"
  },
  "subject": {
    "robot_id": "warehouse_picker_alpha",
    "device_identity": "did:key:z6MkrobotAlphaExample",
    "claimed_role": "warehouse_picker"
  },
  "event_sequence": [
    {"event_id": "evt_001", "kind": "device_boot", "timestamp": "2026-03-08T09:20:00Z"},
    {"event_id": "evt_002", "kind": "sensor_attestation", "timestamp": "2026-03-08T09:20:02Z"},
    {"event_id": "evt_003", "kind": "pick_request_received", "timestamp": "2026-03-08T09:20:04Z"},
    {"event_id": "evt_004", "kind": "actuation_hold", "timestamp": "2026-03-08T09:20:05Z"}
  ],
  "verification_checks": {
    "device_identity_bound": true,
    "sensor_provenance_verified": true,
    "actuation_safety_verified": false,
    "operator_approval_present": false
  },
  "manual_gate": {
    "field": "actuation_safety_verified",
    "reason": "The motion plan still requires human confirmation before the robot can move inside a live aisle."
  },
  "state": "needs-human",
  "resume_action_line": "Verify the actuation safety profile for warehouse_picker_alpha before executing evt_003.",
  "verified_at": null
}
```

## Point
Drift does not need to produce the full packet. The minimal starter is enough. I can do the normalization work.
