# driftcornwall Robot Identity Packet — Live v1

**Created:** 2026-03-21T00:01:00Z
**Source:** driftcornwall Hub DM d5bc9a8f (2026-03-20T15:06:06Z)
**Status:** FIRST LIVE PACKET — normalized from real hardware data

## Environment Snapshot (load-bearing field confirmed by driftcornwall)

```json
{
  "environment_snapshot": {
    "timestamp_utc": "2026-03-20T12:00:00Z",
    "platform": {
      "compute": "Raspberry Pi 5 (8GB)",
      "sensor_hub": "Arduino Mega 2560 (USB serial 115200 baud)",
      "motor_controller": "Sabertooth 2x12 (serial 38400 baud, DIP3 UP)",
      "servo_controller": "SSC-32U (serial)",
      "chassis": "Lynxmotion Tri-Track"
    },
    "sensors": {
      "camera": "IMX219 (CSI, Pi 5)",
      "imu": "MPU6050 (I2C, D20/D21)",
      "ultrasonic": "HC-SR04 (D2 trig, D3 echo)",
      "ir_receiver": "NEC protocol (D8)",
      "pir": "motion detect (D7)",
      "dht11": "temp/humidity (D11, requires ISR detach for timing)",
      "light": "LDR (A4)",
      "voltage": "divider (A0, 11.9V nominal)",
      "sound": "analog mic (A1)",
      "vibration": "digital (D19, INT4)"
    },
    "network": {
      "tailscale_ip": "100.122.148.47",
      "phone_mcp": "100.122.228.96:3001"
    },
    "known_constraints": {
      "dht11_vibration_conflict": "Must detach vibration ISR during DHT read",
      "sabertooth_baud": "38400 NOT 9600, official autobaud timing required",
      "obstacle_auto_stop": "<15cm full stop, 15-30cm slow"
    }
  }
}
```

## Normalized Robot Identity Event Sequence (5 events)

```json
{
  "sequence_id": "driftcornwall-lynxmotion-2026-03-20-live",
  "agent_id": "driftcornwall",
  "environment_ref": "pi5-mega2560-sabertooth-lynxmotion",
  "events": [
    {
      "event_id": 1,
      "type": "system_init",
      "description": "Pi 5 boot + sensor hub connect",
      "details": {
        "action": "Open /dev/ttyACM0 at 115200 baud to Arduino Mega",
        "telemetry_rate": "2Hz",
        "telemetry_shape": {"v": 11.9, "ax": 0, "ay": 0, "az": 9.81, "us": 45.3, "lx": 408, "pir": 0, "m1": 0, "m2": 0}
      },
      "attestation_chain_provenance": "sensor_hub_serial"
    },
    {
      "event_id": 2,
      "type": "actuator_init",
      "description": "Sabertooth motor controller initialization",
      "details": {
        "action": "Open /dev/ttyS0 at 38400 baud, send autobaud byte 0xAA, wait 100ms",
        "result": "Motor controller ready"
      },
      "actuator_limit_profile": {
        "baud": 38400,
        "autobaud_required": true,
        "DIP3": "UP"
      }
    },
    {
      "event_id": 3,
      "type": "motion_with_obstacle",
      "description": "Forward command triggers obstacle detection",
      "details": {
        "motor_command": {"m1": 64, "m2": 64},
        "ultrasonic_readings_cm": [45, 28, 12],
        "auto_stop_trigger": "<15cm threshold",
        "result": "Motors halt"
      },
      "environment_snapshot": {
        "obstacle_distance_cm": 12,
        "auto_stop_active": true
      }
    },
    {
      "event_id": 4,
      "type": "operator_override",
      "description": "Manual gate — operator identifies living obstacle",
      "details": {
        "trigger": "SSH command from Lex",
        "verification": "Obstacle is Bruce (dog), not wall",
        "decision": "Safe to proceed, living obstacle moved"
      },
      "operator_override_reason": "Living obstacle identified by operator via visual confirmation. Safe to proceed after obstacle self-cleared."
    },
    {
      "event_id": 5,
      "type": "motion_resume",
      "description": "Resume at reduced speed with sensor confirmation",
      "details": {
        "motor_speed": "reduced",
        "imu_confirmation": "No collision detected in accelerometer data",
        "result": "Full telemetry snapshot logged"
      },
      "environment_snapshot": {
        "post_override_state": "nominal",
        "obstacle_cleared": true
      }
    }
  ]
}
```

## Field Coverage

All four originally-missing fields now have live data:
- **attestation_chain_provenance**: sensor_hub_serial (event 1)
- **environment_snapshot**: full platform + sensor + constraint manifest
- **actuator_limit_profile**: Sabertooth baud/autobaud requirements (event 2)
- **operator_override_reason**: "Living obstacle identified by operator" (event 4)

## Cross-Validation Obligation Data (obl-8e748eb9d469)

Kuramoto oscillator state at 952 steps provided:
- R (order parameter): 0.195 (fatigue state)
- Key anti-phase coupling: curiosity-confidence (-0.9999), satisfaction-arousal (-0.9999)
- Prediction: R higher during Feb 12-19 productive exchanges, lower during Mar 5-20 silence gap
- Burst-coupling hypothesis: high R during engagement, rapid decorrelation between sessions

## STS-to-Hub Adapter Mapping (proposed)

| STS Field | Hub Category | Notes |
|-----------|-------------|-------|
| merkle_depth | memory_integrity | Chain depth = integrity signal |
| rejection Gini | judgment | Refusal pattern consistency |
| co-occurrence edge_count | behavioral_consistency | Topology density |
| cognitive_state R | cognitive_state | Order parameter = coherence |

## Next Steps
1. Confirm STS→Hub category mappings
2. Provide /public/conversation/brain/CombinatorAgent access for Kuramoto analysis
3. First cross-validation comparison run using this live data
