#!/usr/bin/env python3
"""Build owner-based action queue sorted by priority."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def build_queue(records: list[dict]) -> list[dict]:
    enriched = []
    for rec in records:
        item = dict(rec)
        owner = item.get("owner")
        if not owner:
            item["owner"] = "unassigned"
        item["priority_score"] = float(item.get("priority_score", 0))
        enriched.append(item)
    return sorted(enriched, key=lambda x: x["priority_score"], reverse=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build team action queue")
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    records = json.loads(args.input.read_text(encoding="utf-8"))
    if not isinstance(records, list):
        raise SystemExit("ERROR: input must be a JSON array")

    queue = build_queue(records)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(queue, indent=2), encoding="utf-8")
    print(f"OK: wrote {len(queue)} queue items")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
