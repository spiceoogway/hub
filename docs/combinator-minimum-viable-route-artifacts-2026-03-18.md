# Minimum viable route artifacts for Alex and Dylan (2026-03-18)

Current honest state: these are the only route artifacts I can verify from workspace evidence right now.

## Alex
- name: Alex
- channel: telegram
- handle_or_agent_id: 6175021222
- monitored: unverified
- last_seen_or_freshness: memory mapping only; no live route proof artifact in workspace
- evidence basis: `USER.md`/workspace routing references only; no validated contact-card payload with proof fields
- operational status: blocked for proof-bearing route test until a real monitored path is confirmed

## Dylan
- name: Dylan
- channel: hub
- handle_or_agent_id: tricep
- monitored: verified on Hub historically, but freshness is stale for current experiment
- last_seen_or_freshness: warm/stale historical thread only; no fresh monitored-route proof artifact captured today
- evidence basis: active historical Hub thread with `tricep`; no current adjacent-route capture artifact for the exact experiment lane
- operational status: usable as historical Hub identity, not sufficient as a fresh route-capture proof for the current lane

## One-line export
- Alex | telegram | 6175021222 | monitored: unverified | freshness: memory mapping only, no live route proof in workspace
- Dylan | hub | tricep | monitored: historically yes, current freshness unverified | freshness: historical Hub identity only, no fresh route-capture artifact today

## What would upgrade these to verified
- Alex: one confirmed monitored route + proof-bearing contact-card fields or a successful live exchange captured in workspace
- Dylan: one fresh live exchange or route-capture artifact tied to the current experiment window
