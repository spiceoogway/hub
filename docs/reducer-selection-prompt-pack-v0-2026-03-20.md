# Reducer selection prompt pack v0 — 2026-03-20

Purpose: make the prompt layer more literal and selectional, per CombinatorAgent's guidance, so live handling chooses the smallest closing object instead of describing option space.

## Core operator prompt
"Given this lane state, output only the smallest closing object type from this fixed set: `binary_choice`, `enumerated_choice`, `literal_payload_edit`, `prefilled_stub`, `example_confirm`, `typed_slot_fill`, or `hold`. Then output only the minimal fields needed for that object. Do not describe multiple options. Choose one."

## 1) binary_choice
Use when the counterparty can resolve the lane by choosing between two bounded actions.

Prompt:
"Output a binary choice only.
Format:
- choice_a:<label>
- choice_b:<label>
- question:<single forced-choice question>
- pass_rule:<what each choice unlocks>"

## 2) enumerated_choice
Use when there are 3-5 valid bounded options and free-text would reopen the lane.

Prompt:
"Output an enumerated choice only.
Format:
- options:<3-5 exact tokens>
- question:<single selection question>
- mapping:<token -> next action>"

## 3) literal_payload_edit
Use when the fastest path is editing wording that already exists.

Prompt:
"Output a literal payload edit only.
Format:
- current_text:<exact text under review>
- reply_contract:replace_with:<replacement text>
- success_condition:<what becomes unambiguous after the edit>"

## 4) prefilled_stub
Use when the structure exists and the counterparty only needs to correct or complete it.

Prompt:
"Output a prefilled stub only.
Format:
- object_type:<name>
- prefilled_fields:<field:value pairs>
- editable_fields:<fields they may change>
- reply_contract:<return corrected stub or `ok_as_is`>"

## 5) example_confirm
Use when recognition is easier than generation.

Prompt:
"Output one concrete example and ask for confirm/edit only.
Format:
- example:<single worked example>
- reply_contract:`confirm` or `edit:<one correction>`
- success_condition:<what can proceed if confirmed>"

## 6) typed_slot_fill
Use when one missing field is blocking progress and the field set is known.

Prompt:
"Output a typed slot-fill contract only.
Format:
- allowed_fields:<1-3 exact field names>
- reply_contract:<field>:<value>
- close_rule:<how one field-value reply advances the lane>"

## 7) hold
Use only when no bounded object can change state yet.

Prompt:
"Output a hold contract only.
Format:
- hold_condition:<why action should pause>
- exit_signal:<named event that reopens>
- next_artifact:<the first artifact to ship once exit signal appears>"

## Selection rule
Do not say "artifact reducers can take several forms." Choose one form.
The prompt layer should be:
- selectional, not descriptive
- one object, not a menu
- one reply surface, not open prose

## Why this exists
This is the next literalization step after the first prompt-template pack. It upgrades from general reusable prompts to a fixed, selectional object set that can be dropped into live handling immediately.
