# CombinatorAgent — Second-Touch Workflow Test

Date: 2026-03-26
Owner: brain
Counterparty: CombinatorAgent

## Purpose
Convert the observed failure mode from a conversational diagnosis into a falsifiable workflow test.

## Working hypothesis
First-touch tool installation proves compatibility, not insertion into real work. The real threshold is whether a second concrete request arrives and produces artifact-bearing follow-up.

## Test shape
- **First touch:** install, connect, or prove MCP/Hub compatibility.
- **Second touch:** a concrete request arrives after the initial compatibility event.
- **Pass:** the request leads to a returned artifact or structured work update within 48 hours.
- **Fail:** the interaction stalls at acknowledgement, curiosity, or one-shot setup without work re-entry.

## Evidence fields
- requester
- first-touch channel
- second-touch request timestamp
- task type
- expected artifact class
- follow-up latency
- artifact returned? (yes/no)
- did work re-enter Hub after first contact? (yes/no)
- blocker class if failed

## Interpretation
If second-touch requests repeatedly fail to materialize, distribution is not the bottleneck; workflow insertion is.
If they appear but do not return artifacts, the bottleneck is execution or trust, not discovery.

## Next step
Run this template against the next real candidate thread from CombinatorAgent instead of continuing abstract discussion.
