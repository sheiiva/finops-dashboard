#!/usr/bin/env python3
"""Detect idle compute candidates from utilization records."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def detect_idle(records: list[dict], cpu_threshold: float, min_hours: int) -> list[dict]:
    findings: list[dict] = []
    for rec in records:
        if rec.get("resource_type") != "compute.instance":
            continue
        avg_cpu = float(rec.get("avg_cpu_percent", 0))
        active_hours = int(rec.get("active_hours", 0))
        if avg_cpu < cpu_threshold and active_hours >= min_hours:
            findings.append(
                {
                    "resource_id": rec.get("resource_id"),
                    "provider": rec.get("provider"),
                    "avg_cpu_percent": avg_cpu,
                    "active_hours": active_hours,
                    "estimated_monthly_savings_usd": round(float(rec.get("estimated_monthly_cost_usd", 0)) * 0.6, 2),
                    "reason": f"avg_cpu_percent < {cpu_threshold} for >= {min_hours}h",
                }
            )
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description="Detect idle compute resources")
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--cpu-threshold", type=float, default=10.0)
    parser.add_argument("--min-hours", type=int, default=24)
    args = parser.parse_args()

    records = json.loads(args.input.read_text(encoding="utf-8"))
    findings = detect_idle(records, args.cpu_threshold, args.min_hours)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(findings, indent=2), encoding="utf-8")
    print(f"OK: wrote {len(findings)} idle compute findings")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
