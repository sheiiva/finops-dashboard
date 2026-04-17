#!/usr/bin/env python3
"""Data quality and freshness checks for collector outputs."""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path

REQUIRED_FIELDS = (
    "provider",
    "resource_id",
    "resource_type",
    "environment",
    "owner",
    "service",
    "region",
    "cost_amount",
    "cost_currency",
    "usage_quantity",
    "usage_unit",
    "timestamp",
)


def _load(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError(f"{path} must contain a JSON array")
    return data


def _missing_fields(record: dict) -> list[str]:
    missing = []
    for key in REQUIRED_FIELDS:
        value = record.get(key)
        if value is None or (isinstance(value, str) and not value.strip()):
            missing.append(key)
    return missing


def _freshness_minutes(record: dict) -> float:
    ts = datetime.fromisoformat(record["timestamp"].replace("Z", "+00:00"))
    now = datetime.now(UTC)
    return (now - ts).total_seconds() / 60


def build_report(records: list[dict], freshness_sla_minutes: int) -> dict:
    total = len(records)
    null_field_violations = 0
    stale_records = 0

    for rec in records:
        if _missing_fields(rec):
            null_field_violations += 1
        try:
            if _freshness_minutes(rec) > freshness_sla_minutes:
                stale_records += 1
        except Exception:
            stale_records += 1

    completeness_percent = 100.0 if total == 0 else ((total - null_field_violations) / total) * 100
    freshness_percent = 100.0 if total == 0 else ((total - stale_records) / total) * 100
    return {
        "total_records": total,
        "null_field_violations": null_field_violations,
        "stale_records": stale_records,
        "completeness_percent": round(completeness_percent, 2),
        "freshness_percent": round(freshness_percent, 2),
        "freshness_sla_minutes": freshness_sla_minutes,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate data quality report")
    parser.add_argument("--input", required=True, type=Path, help="Path to normalized records JSON array")
    parser.add_argument("--output", required=True, type=Path, help="Path to output quality report JSON")
    parser.add_argument("--freshness-sla-minutes", type=int, default=180, help="Freshness SLA in minutes")
    args = parser.parse_args()

    records = _load(args.input)
    report = build_report(records, args.freshness_sla_minutes)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"OK: wrote quality report to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
