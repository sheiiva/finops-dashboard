#!/usr/bin/env python3
"""Detect orphaned storage artifacts from inventory records."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def detect_orphaned(records: list[dict]) -> list[dict]:
    findings: list[dict] = []
    for rec in records:
        if rec.get("resource_type") not in {"storage.disk", "storage.snapshot", "storage.bucket"}:
            continue
        attached = bool(rec.get("attached", False))
        last_access_days = int(rec.get("last_access_days", 0))
        monthly_cost = float(rec.get("estimated_monthly_cost_usd", 0))

        is_orphaned = (not attached and rec.get("resource_type") != "storage.bucket") or (
            rec.get("resource_type") == "storage.bucket" and last_access_days > 90
        )
        if is_orphaned:
            findings.append(
                {
                    "resource_id": rec.get("resource_id"),
                    "provider": rec.get("provider"),
                    "resource_type": rec.get("resource_type"),
                    "last_access_days": last_access_days,
                    "estimated_monthly_savings_usd": round(monthly_cost * 0.8, 2),
                    "reason": "orphaned or stale storage artifact",
                }
            )
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description="Detect orphaned storage artifacts")
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    records = json.loads(args.input.read_text(encoding="utf-8"))
    findings = detect_orphaned(records)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(findings, indent=2), encoding="utf-8")
    print(f"OK: wrote {len(findings)} orphaned storage findings")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
