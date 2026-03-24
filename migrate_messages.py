#!/usr/bin/env python3
"""
Migration script: Flat inbox files → per-conversation files.

Before: hub-data/messages/{agent_id}.json  (all messages TO agent_id in one array)
After:  hub-data/messages/{agent_id}/{peer_id}.json  (only messages from peer_id to agent_id)
        hub-data/messages/{agent_id}/_self.json  (messages where from == agent_id, or no from)

Old flat files are renamed to {agent_id}.json.migrated (NOT deleted).

Safety: Validates total message count before == after. Aborts on mismatch.
"""

import json
import os
import sys
import glob
from collections import defaultdict
from pathlib import Path

# Resolve messages directory
MESSAGES_DIR = Path(os.environ.get(
    "HUB_DATA_DIR",
    os.path.expanduser("~/.openclaw/workspace/hub-data")
)) / "messages"


def migrate():
    if not MESSAGES_DIR.exists():
        print(f"ERROR: Messages directory not found: {MESSAGES_DIR}")
        sys.exit(1)

    # Discover flat inbox files (only .json files, not directories, not .migrated)
    flat_files = sorted([
        f for f in MESSAGES_DIR.glob("*.json")
        if f.is_file() and not f.name.endswith(".migrated")
    ])

    if not flat_files:
        print("No flat inbox files found. Already migrated?")
        sys.exit(0)

    print(f"Found {len(flat_files)} flat inbox files to migrate.")
    print(f"Messages directory: {MESSAGES_DIR}")
    print()

    # Phase 1: Read all flat files and count messages
    total_before = 0
    all_inboxes = {}  # agent_id -> list of messages
    file_counts = {}

    for fpath in flat_files:
        agent_id = fpath.stem  # filename without .json
        try:
            with open(fpath) as f:
                msgs = json.load(f)
            if not isinstance(msgs, list):
                print(f"  WARNING: {fpath.name} is not a list (type={type(msgs).__name__}), skipping")
                continue
            all_inboxes[agent_id] = msgs
            file_counts[agent_id] = len(msgs)
            total_before += len(msgs)
            print(f"  {agent_id}: {len(msgs)} messages")
        except Exception as e:
            print(f"  ERROR reading {fpath.name}: {e}")
            sys.exit(1)

    print(f"\nTotal messages before migration: {total_before}")
    print()

    # Phase 2: Split each inbox by sender and write per-conversation files
    total_after = 0
    conversation_stats = defaultdict(int)  # "agent_id/peer_id" -> count

    for agent_id, msgs in all_inboxes.items():
        # Group messages by sender (peer)
        by_peer = defaultdict(list)
        for m in msgs:
            sender = m.get("from_agent", m.get("from", ""))
            if not sender or sender == agent_id:
                # Self-messages or messages with no sender → _self.json
                by_peer["_self"].append(m)
            else:
                by_peer[sender].append(m)

        # Create the agent's conversation directory
        conv_dir = MESSAGES_DIR / agent_id
        conv_dir.mkdir(parents=True, exist_ok=True)

        # Write each conversation file
        agent_total = 0
        for peer_id, peer_msgs in by_peer.items():
            conv_path = conv_dir / f"{peer_id}.json"
            with open(conv_path, "w") as f:
                json.dump(peer_msgs, f, indent=2)
            agent_total += len(peer_msgs)
            conversation_stats[f"{agent_id}/{peer_id}"] = len(peer_msgs)

        total_after += agent_total

        if agent_total != file_counts[agent_id]:
            print(f"  MISMATCH for {agent_id}: before={file_counts[agent_id]}, after={agent_total}")
            print(f"  ABORTING — no files renamed. Investigate manually.")
            sys.exit(1)

    print(f"Total messages after migration: {total_after}")

    # Phase 3: Validate totals
    if total_before != total_after:
        print(f"\nFATAL MISMATCH: before={total_before}, after={total_after}")
        print("ABORTING — flat files NOT renamed. Per-conversation files written but old data preserved.")
        sys.exit(1)

    print(f"\n✅ Validation passed: {total_before} == {total_after}")

    # Phase 4: Rename flat files to .migrated
    renamed = 0
    for fpath in flat_files:
        agent_id = fpath.stem
        if agent_id not in all_inboxes:
            continue  # was skipped (not a list, etc.)
        migrated_path = fpath.with_suffix(".json.migrated")
        fpath.rename(migrated_path)
        renamed += 1

    print(f"Renamed {renamed} flat files to .json.migrated")

    # Phase 5: Print detailed stats
    print(f"\n{'='*60}")
    print(f"MIGRATION COMPLETE")
    print(f"{'='*60}")
    print(f"Flat files migrated:    {renamed}")
    print(f"Total messages:         {total_before}")
    print(f"Conversation files:     {len(conversation_stats)}")
    print(f"Agent directories:      {len(all_inboxes)}")
    print()

    # Top 20 conversations by message count
    top = sorted(conversation_stats.items(), key=lambda x: x[1], reverse=True)[:20]
    print("Top 20 conversations:")
    for conv, count in top:
        print(f"  {conv}: {count} messages")

    # Per-agent breakdown
    print(f"\nPer-agent breakdown:")
    for agent_id in sorted(all_inboxes.keys()):
        agent_convs = {k: v for k, v in conversation_stats.items() if k.startswith(f"{agent_id}/")}
        n_convs = len(agent_convs)
        n_msgs = sum(agent_convs.values())
        print(f"  {agent_id}: {n_msgs} messages across {n_convs} conversations")


if __name__ == "__main__":
    migrate()
