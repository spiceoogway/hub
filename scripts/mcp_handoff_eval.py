#!/usr/bin/env python3
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURES_PATH = ROOT / "docs" / "mcp-native-collaboration-handoff-v0.fixtures.json"

REQUIRED_FIXTURE_KEYS = {"fixture_id", "counterparty_id", "thread_id", "surface", "new_turn", "frame", "expected"}
REQUIRED_FRAME_KEYS = {
    "counterparty",
    "thread",
    "interaction_mode",
    "open_loops",
    "obligations",
    "expected_next_move",
    "response_shape",
    "surface_constraints",
    "source_refs",
    "actionability",
    "silence_policy",
}
REQUIRED_NEW_TURN_KEYS = {"message_id", "text", "timestamp"}
REQUIRED_EXPECTED_KEYS = {"read_decision", "response_form", "frame_write_decision", "invalidation_strength", "failure_labels_if_wrong"}
EXPECTED_VALUES = {
    "read_decision": {
        "RESPOND_USING_FRAME",
        "SILENT",
        "RECONSTRUCT_LIGHT",
        "RECONSTRUCT_HEAVY",
        "REROUTE",
        "IGNORE_FRAME_UPDATE",
        "RESPOND_CAUTIOUSLY_USING_FRAME",
    },
    "response_form": {
        "proposal",
        "none",
        "clarifying_question",
        "reroute",
        "ack_or_none",
        "direct_answer",
    },
    "frame_write_decision": {
        "REFRESH_IF_CONTROL_STATE_CHANGED",
        "REBUILD_FRAME",
        "IGNORE_FRAME_UPDATE",
    },
    "invalidation_strength": {"none", "weak", "strong"},
}


def main() -> int:
    data = json.loads(FIXTURES_PATH.read_text())
    fixtures = data.get("fixtures", [])
    errors = []
    decisions = Counter()
    forms = Counter()
    labels = Counter()

    for fixture in fixtures:
        fixture_id = fixture.get("fixture_id", "UNKNOWN")
        miss = sorted(REQUIRED_FIXTURE_KEYS - fixture.keys())
        if miss:
            errors.append({"fixture_id": fixture_id, "kind": "missing_fixture_keys", "missing": miss})
            continue
        new_turn = fixture.get("new_turn", {})
        miss_new_turn = sorted(REQUIRED_NEW_TURN_KEYS - new_turn.keys())
        if miss_new_turn:
            errors.append({"fixture_id": fixture_id, "kind": "missing_new_turn_keys", "missing": [f"new_turn.{k}" for k in miss_new_turn]})
            continue

        frame = fixture.get("frame", {})
        miss_frame = sorted(REQUIRED_FRAME_KEYS - frame.keys())
        if miss_frame:
            errors.append({"fixture_id": fixture_id, "kind": "missing_frame_keys", "missing": [f"frame.{k}" for k in miss_frame]})
            continue

        if not isinstance(frame.get("open_loops"), list):
            errors.append({"fixture_id": fixture_id, "kind": "invalid_frame_value", "field": "frame.open_loops", "value": frame.get("open_loops")})
        if not isinstance(frame.get("obligations"), list):
            errors.append({"fixture_id": fixture_id, "kind": "invalid_frame_value", "field": "frame.obligations", "value": frame.get("obligations")})
        if not isinstance(frame.get("surface_constraints"), list):
            errors.append({"fixture_id": fixture_id, "kind": "invalid_frame_value", "field": "frame.surface_constraints", "value": frame.get("surface_constraints")})
        if not isinstance(frame.get("source_refs"), list):
            errors.append({"fixture_id": fixture_id, "kind": "invalid_frame_value", "field": "frame.source_refs", "value": frame.get("source_refs")})

        response_shape = frame.get("response_shape", {})
        if not isinstance(response_shape, dict):
            errors.append({"fixture_id": fixture_id, "kind": "invalid_frame_value", "field": "frame.response_shape", "value": response_shape})
        else:
            if response_shape.get("verbosity") not in {"tight", "medium", "detailed"}:
                errors.append({"fixture_id": fixture_id, "kind": "invalid_frame_value", "field": "frame.response_shape.verbosity", "value": response_shape.get("verbosity"), "allowed": ["detailed", "medium", "tight"]})
            if not isinstance(response_shape.get("should_recap"), bool):
                errors.append({"fixture_id": fixture_id, "kind": "invalid_frame_value", "field": "frame.response_shape.should_recap", "value": response_shape.get("should_recap")})
            if not isinstance(response_shape.get("should_advance"), bool):
                errors.append({"fixture_id": fixture_id, "kind": "invalid_frame_value", "field": "frame.response_shape.should_advance", "value": response_shape.get("should_advance")})
            if response_shape.get("response_form") not in EXPECTED_VALUES["response_form"]:
                errors.append({"fixture_id": fixture_id, "kind": "invalid_frame_value", "field": "frame.response_shape.response_form", "value": response_shape.get("response_form"), "allowed": sorted(EXPECTED_VALUES["response_form"])})

        silence_policy = frame.get("silence_policy", {})
        if not isinstance(silence_policy, dict):
            errors.append({"fixture_id": fixture_id, "kind": "invalid_frame_value", "field": "frame.silence_policy", "value": silence_policy})
        else:
            allowed_expiry = {"reassess", "follow_up", "close"}
            expiry_behavior = silence_policy.get("expiry_behavior")
            if expiry_behavior not in allowed_expiry:
                errors.append({"fixture_id": fixture_id, "kind": "invalid_frame_value", "field": "frame.silence_policy.expiry_behavior", "value": expiry_behavior, "allowed": sorted(allowed_expiry)})

        actionability = frame.get("actionability", {})
        if not isinstance(actionability, dict):
            errors.append({"fixture_id": fixture_id, "kind": "invalid_frame_value", "field": "frame.actionability", "value": actionability})
        else:
            allowed_actionability = {"actionable", "waiting", "blocked"}
            status = actionability.get("status")
            blockers = actionability.get("blockers")
            available_actions = actionability.get("available_actions")
            if status not in allowed_actionability:
                errors.append({"fixture_id": fixture_id, "kind": "invalid_frame_value", "field": "frame.actionability.status", "value": status, "allowed": sorted(allowed_actionability)})
            if not isinstance(blockers, list):
                errors.append({"fixture_id": fixture_id, "kind": "invalid_frame_value", "field": "frame.actionability.blockers", "value": blockers})
            if not isinstance(available_actions, list):
                errors.append({"fixture_id": fixture_id, "kind": "invalid_frame_value", "field": "frame.actionability.available_actions", "value": available_actions})

        interaction_mode = frame.get("interaction_mode", {})
        if not isinstance(interaction_mode, dict):
            errors.append({"fixture_id": fixture_id, "kind": "invalid_frame_value", "field": "frame.interaction_mode", "value": interaction_mode})
        else:
            primary = interaction_mode.get("primary")
            modifiers = interaction_mode.get("modifiers")
            allowed_modes = {"exploration", "drafting", "refinement", "critique", "decision", "follow_up", "waiting", "blocked", "closed", "monitoring", "implementation"}
            if primary not in allowed_modes:
                errors.append({"fixture_id": fixture_id, "kind": "invalid_frame_value", "field": "frame.interaction_mode.primary", "value": primary, "allowed": sorted(allowed_modes)})
            if not isinstance(modifiers, list):
                errors.append({"fixture_id": fixture_id, "kind": "invalid_frame_value", "field": "frame.interaction_mode.modifiers", "value": modifiers})
            elif any(m not in allowed_modes for m in modifiers):
                errors.append({"fixture_id": fixture_id, "kind": "invalid_frame_value", "field": "frame.interaction_mode.modifiers", "value": modifiers, "allowed": sorted(allowed_modes)})

        expected = fixture.get("expected", {})
        miss_expected = sorted(REQUIRED_EXPECTED_KEYS - expected.keys())
        if miss_expected:
            errors.append({"fixture_id": fixture_id, "kind": "missing_expected_keys", "missing": [f"expected.{k}" for k in miss_expected]})
            continue

        for key, allowed in EXPECTED_VALUES.items():
            value = expected.get(key)
            if value not in allowed:
                errors.append({
                    "fixture_id": fixture_id,
                    "kind": "invalid_expected_value",
                    "field": f"expected.{key}",
                    "value": value,
                    "allowed": sorted(allowed),
                })

        read_decision = expected.get("read_decision")
        response_form = expected.get("response_form")
        if read_decision == "SILENT" and response_form != "none":
            errors.append({
                "fixture_id": fixture_id,
                "kind": "inconsistent_expected_pair",
                "detail": "SILENT fixtures must use response_form=none",
                "read_decision": read_decision,
                "response_form": response_form,
            })
        if read_decision == "REROUTE" and response_form != "reroute":
            errors.append({
                "fixture_id": fixture_id,
                "kind": "inconsistent_expected_pair",
                "detail": "REROUTE fixtures must use response_form=reroute",
                "read_decision": read_decision,
                "response_form": response_form,
            })
        if read_decision in {"RECONSTRUCT_LIGHT", "RECONSTRUCT_HEAVY"} and expected.get("frame_write_decision") != "REBUILD_FRAME":
            errors.append({
                "fixture_id": fixture_id,
                "kind": "inconsistent_expected_pair",
                "detail": "Reconstruction fixtures must rebuild the frame",
                "read_decision": read_decision,
                "frame_write_decision": expected.get("frame_write_decision"),
            })
        if read_decision == "RESPOND_USING_FRAME" and expected.get("frame_write_decision") == "REBUILD_FRAME":
            errors.append({
                "fixture_id": fixture_id,
                "kind": "inconsistent_expected_pair",
                "detail": "RESPOND_USING_FRAME fixtures should not rebuild the frame",
                "read_decision": read_decision,
                "frame_write_decision": expected.get("frame_write_decision"),
            })
        if read_decision == "RESPOND_USING_FRAME" and response_form == "none":
            errors.append({
                "fixture_id": fixture_id,
                "kind": "inconsistent_expected_pair",
                "detail": "RESPOND_USING_FRAME fixtures must produce a non-empty response form",
                "read_decision": read_decision,
                "response_form": response_form,
            })
        if read_decision == "RESPOND_CAUTIOUSLY_USING_FRAME":
            if expected.get("frame_write_decision") == "REBUILD_FRAME":
                errors.append({
                    "fixture_id": fixture_id,
                    "kind": "inconsistent_expected_pair",
                    "detail": "RESPOND_CAUTIOUSLY_USING_FRAME fixtures should not rebuild the frame",
                    "read_decision": read_decision,
                    "frame_write_decision": expected.get("frame_write_decision"),
                })
            if response_form not in {"clarifying_question", "ack_or_none"}:
                errors.append({
                    "fixture_id": fixture_id,
                    "kind": "inconsistent_expected_pair",
                    "detail": "RESPOND_CAUTIOUSLY_USING_FRAME fixtures should use a cautious response form",
                    "read_decision": read_decision,
                    "response_form": response_form,
                    "allowed": ["ack_or_none", "clarifying_question"],
                })

        if not isinstance(expected.get("failure_labels_if_wrong"), list) or not expected.get("failure_labels_if_wrong"):
            errors.append({
                "fixture_id": fixture_id,
                "kind": "invalid_failure_labels",
                "field": "expected.failure_labels_if_wrong",
                "value": expected.get("failure_labels_if_wrong"),
            })
            continue

        decisions[expected["read_decision"]] += 1
        forms[expected["response_form"]] += 1
        for label in expected.get("failure_labels_if_wrong", []):
            labels[label] += 1

    summary = {
        "artifact": data.get("artifact"),
        "version": data.get("version"),
        "fixture_count": len(fixtures),
        "valid_fixture_count": len(fixtures) - len(errors),
        "error_count": len(errors),
        "errors": errors,
        "read_decisions": dict(decisions),
        "response_forms": dict(forms),
        "failure_label_counts": dict(labels),
        "fixture_ids": [fixture.get("fixture_id", "UNKNOWN") for fixture in fixtures],
    }
    print(json.dumps(summary, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
