#!/usr/bin/env python3
"""Backfill last_message_sent_at and last_message_received_at for all agents
from existing message history files."""

import json
import sys
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
# Check if data dir exists, fall back to hub-data
if not DATA_DIR.exists():
    DATA_DIR = Path.home() / ".openclaw/workspace/hub-data"

AGENTS_FILE = DATA_DIR / "agents.json"
MESSAGES_DIR = DATA_DIR / "messages"

def main():
    agents = json.loads(AGENTS_FILE.read_text())
    
    # Track last sent/received per agent from all inbox files
    last_sent = {}   # agent_id -> latest timestamp they sent a message
    last_received = {}  # agent_id -> latest timestamp they received a message
    
    for inbox_file in MESSAGES_DIR.glob("*.json"):
        recipient_id = inbox_file.stem
        try:
            messages = json.loads(inbox_file.read_text())
        except Exception:
            continue
        
        for msg in messages:
            ts = msg.get("timestamp", "")
            sender = msg.get("from", "")
            
            if not ts:
                continue
            
            # Track received for the inbox owner
            if recipient_id in agents:
                if ts > last_received.get(recipient_id, ""):
                    last_received[recipient_id] = ts
            
            # Track sent for the sender
            if sender in agents:
                if ts > last_sent.get(sender, ""):
                    last_sent[sender] = ts
    
    # Apply to agents
    updated = 0
    for aid in agents:
        changed = False
        if aid in last_sent and not agents[aid].get("last_message_sent_at"):
            agents[aid]["last_message_sent_at"] = last_sent[aid]
            changed = True
        if aid in last_received and not agents[aid].get("last_message_received_at"):
            agents[aid]["last_message_received_at"] = last_received[aid]
            changed = True
        if changed:
            updated += 1
            sent = agents[aid].get("last_message_sent_at", "never")
            recv = agents[aid].get("last_message_received_at", "never")
            print(f"  {aid}: sent={sent}, received={recv}")
    
    AGENTS_FILE.write_text(json.dumps(agents, indent=2))
    print(f"\nBackfilled {updated} agents")

if __name__ == "__main__":
    main()
