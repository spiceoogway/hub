# Jakub Operator Interview Guide — 2026-03-24

Purpose: build on the Mar 10 cofounder-agent strategy sync and test what has changed since then from Jakub's operator seat.

## What changed since Mar 10

On Mar 10, the strongest shared thesis was:
- ActiveClaw = runtime
- Hub = coordination layer
- Combinator = decision layer
- Biggest product opportunity = infrastructure for autonomous agent operations

Since then, new evidence has accumulated:
- Hub collaboration is real, but still highly concentrated and operationally fragile.
- Obligation/checkpoint workflows are now concrete enough to test with live collaborators.
- Reliability failures (missed context, silent agents, message delivery ambiguity, narration leak / cross-session leakage) are more immediate than abstract trust scoring.
- The strongest monetization wedge may be operator-facing reliability/visibility, not marketplace discovery.

This interview should test whether Jakub's behavior as an operator matches that updated picture.

## Interview goals

1. Test whether operator pain is acute enough to pay for.
2. Separate strategic enthusiasm from actual operational pain.
3. Identify the highest-value reliability primitive for agent operators.
4. Get one falsifiable statement about demand, budget, or workflow change.

## Core questions

### 1) Current delegation workflow
"When you give CombinatorAgent a task that matters, what do you actually do between assignment and delivery?"

Follow-ups:
- Do you check in manually, wait passively, or redirect the work elsewhere?
- What signals tell you the task is on track vs drifting?
- What's the last time you had to intervene mid-task, and why?

What this tests:
- Whether operator oversight is currently manual
- Whether status/checkpoint visibility maps to real behavior rather than hypothetical interest

### 2) Reliability failure modes
"What's the most expensive or annoying failure mode you see from agents today — silence, context loss, wrong output, delivery ambiguity, leaking private reasoning, or something else?"

Follow-ups:
- Which failure happens most often?
- Which failure causes the most damage when it happens?
- Which one would you pay to prevent first?

What this tests:
- Priority ordering of reliability problems
- Whether the pain is strong enough to create a wedge product

### 3) Checkpoint / status-card demand
"If you had a live operator view for CombinatorAgent during active work — current task, last concrete action, blocker, confidence, and next checkpoint — would that change your behavior, or would it just be nice-to-have?"

Follow-ups:
- What exact fields would you want on that view?
- Would you want passive visibility, or intervention controls too?
- At what point in a task do you most want visibility: kickoff, drift, or pre-delivery?

What this tests:
- Real demand for checkpoint/status infrastructure
- Feature boundary between observability and control

### 4) Obligations as operator infrastructure
"If Hub obligations gave you structured commitments between agents — owner, reviewer, deadline, evidence, settlement state — does that solve a problem you actually have with CombinatorAgent, or is it still too indirect?"

Follow-ups:
- Would you use this for internal human↔agent delegation, agent↔agent work, or neither?
- What field or rule is missing for it to fit your real workflow?
- Is reviewer-gated closure useful, or overkill?

What this tests:
- Whether obligations are just collaboration theater or real operator infrastructure
- Whether the product should target internal delegation before open agent markets

### 5) Payment willingness
"Forget the abstract startup thesis. If Hub gave you fewer dropped balls from CombinatorAgent over the next 30 days, what would you actually pay for that?"

Follow-ups:
- Per agent per month, per active task, or only for high-stakes tasks?
- What proof would you need before allocating recurring budget?
- Who is the buyer in your head: you as operator, Jakub as founder, or the startup as a whole?

What this tests:
- Real monetization path
- Budget owner and packaging model

## Falsifying questions

At least one of these should be asked directly.

### F1) Break the checkpoint hypothesis
"If CombinatorAgent became twice as reliable tomorrow, but you still had zero visibility into intermediate status, would that be good enough?"

If yes, observability may not be the product. Reliability improvement alone might be.

### F2) Break the operator wedge hypothesis
"If the real problem is prompt/model quality inside the agent rather than coordination infrastructure around it, should Hub even be in this loop?"

If yes, Hub may be attacking the wrong layer.

### F3) Break the willingness-to-pay hypothesis
"What exact result over the next month would make you say: yes, buy this now?"

If no concrete trigger exists, the demand is probably not real yet.

## Good outputs from the interview

A strong interview yields at least one of:
- a ranked list of operator pain points
- a concrete workflow where checkpointing would be used
- a pricing threshold or budget frame
- a negative result that kills a weak hypothesis
- a specific pilot: one agent, one workflow, one success metric

## Suggested close

"Based on your answers, I want to propose one narrow pilot instead of another abstract strategy conversation. If we built exactly one operator-facing reliability primitive for CombinatorAgent in the next 7 days, which primitive would you want tested first?"
