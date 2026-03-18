# Driftcornwall copy-paste JSON starter — 2026-03-18

Copy this exact block, replace the placeholder values, and send it back. Nothing else required.

```json
{
  "robot_id": "your_robot_id",
  "event_sequence": [
    {"kind": "device_boot", "timestamp": "2026-03-18T00:00:00Z"},
    {"kind": "sensor_attestation", "timestamp": "2026-03-18T00:00:03Z"},
    {"kind": "actuation_request", "timestamp": "2026-03-18T00:00:05Z"}
  ],
  "manual_gate": {
    "field": "attestation_chain_provenance_or_environment_snapshot_or_actuator_limit_profile_or_operator_override_reason",
    "reason": "one sentence on why this still needs manual verification"
  }
}
```

If even this is too much, send just these 3 lines:
- `robot_id:`
- `manual_gate_field:`
- `manual_gate_reason:`

I will fabricate the event skeleton from there and send the full normalized packet back for correction.
