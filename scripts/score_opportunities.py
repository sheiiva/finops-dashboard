#!/usr/bin/env python3
"""Score optimization opportunities by impact, confidence, and effort."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

CONFIDENCE_MAP = {"low": 0.5, "medium": 0.75, "high": 1.0}
EFFORT_MAP = {"low": 1.0, "medium": 0.7, "high": 0.4}


def score(opportunity: dict) -> dict:
    savings = float(opportunity.get("estimated_monthly_savings_usd", 0))
    confidence = CONFIDENCE_MAP.get(str(opportunity.get("confidence", "medium")).lower(), 0.75)
    effort = EFFORT_MAP.get(str(opportunity.get("effort", "medium")).lower(), 0.7)
    priority_score = round(savings * confidence * effort, 2)

    out = dict(opportunity)
    out["priority_score"] = priority_score
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="Score optimization opportunities")
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    data = json.loads(args.input.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise SystemExit("ERROR: input must be a JSON array")

    scored = sorted((score(item) for item in data), key=lambda x: x["priority_score"], reverse=True)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(scored, indent=2), encoding="utf-8")
    print(f"OK: wrote {len(scored)} scored opportunities")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
