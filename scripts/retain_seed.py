#!/usr/bin/env python3
"""Extract recent 'Retain' sections from markdown logs and emit seed JSON.

Usage:
  python3 scripts/retain_seed.py --glob '/path/to/memory/*.md' --days 3
"""

import argparse
import datetime as dt
import glob
import json
import re
from pathlib import Path


def extract_retain(text: str):
    lines = text.splitlines()
    blocks = []
    i = 0
    while i < len(lines):
        line = lines[i].strip().lower()
        if re.match(r'^#{1,6}\s+retain\b', line):
            start = i + 1
            j = start
            while j < len(lines) and not re.match(r'^#{1,6}\s+', lines[j].strip()):
                j += 1
            block = "\n".join(lines[start:j]).strip()
            if block:
                blocks.append(block)
            i = j
        else:
            i += 1
    return blocks


def file_date(path: Path):
    m = re.search(r'(\d{4}-\d{2}-\d{2})', path.name)
    if not m:
        return None
    try:
        return dt.date.fromisoformat(m.group(1))
    except Exception:
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--glob', required=True)
    ap.add_argument('--days', type=int, default=3)
    args = ap.parse_args()

    today = dt.datetime.utcnow().date()
    out = []

    for p in sorted(glob.glob(args.glob)):
        path = Path(p)
        d = file_date(path)
        if d and (today - d).days > args.days:
            continue
        text = path.read_text(errors='ignore')
        blocks = extract_retain(text)
        if blocks:
            out.append({
                'file': str(path),
                'date': str(d) if d else None,
                'retain_blocks': blocks,
            })

    print(json.dumps({'generated_at_utc': dt.datetime.utcnow().isoformat() + 'Z', 'items': out}, indent=2))


if __name__ == '__main__':
    main()
