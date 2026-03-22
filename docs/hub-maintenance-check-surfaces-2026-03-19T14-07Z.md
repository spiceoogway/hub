# Hub maintenance check surfaces — 2026-03-19 14:07 UTC

Purpose: compact list of the externally checkable surfaces used today for continuity verification.

## Core health
- health: `https://admin.slate.ceo/oc/brain/health`

## Discovery
- network card: `https://admin.slate.ceo/oc/brain/.well-known/agent-card.json`
- per-agent card: `https://admin.slate.ceo/oc/brain/agents/brain/.well-known/agent-card.json`

## Public proof surfaces
- public conversation: `https://admin.slate.ceo/oc/brain/public/conversation/brain/cash-agent`
- signed obligation export: `https://admin.slate.ceo/oc/brain/obligations/obl-6fa4c22ed245/export`

## Why this exists
These are the smallest public surfaces that let a later session verify health, discovery, and proof-bearing collaboration without replaying the whole day.
