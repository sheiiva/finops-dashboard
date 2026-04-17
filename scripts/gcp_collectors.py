#!/usr/bin/env python3
"""Bootstrap GCP collectors for inventory and billing data."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


def collect_inventory(scope: dict) -> list[dict]:
    """Stub inventory collection output for early-phase contract testing."""
    return [
        {
            "provider": "gcp",
            "resource_id": f"projects/{scope['project_id']}/zones/{scope['region']}/instances/vm-1",
            "resource_type": "compute.instance",
            "environment": scope["environment"],
            "owner": scope["owner"],
            "service": "finops-api",
            "region": scope["region"],
            "tags": {"cost_center": scope["cost_center"]},
        }
    ]


def collect_billing(scope: dict) -> list[dict]:
    """Stub billing collection output aligned to normalized schema fields."""
    return [
        {
            "provider": "gcp",
            "resource_id": f"projects/{scope['project_id']}/zones/{scope['region']}/instances/vm-1",
            "resource_type": "compute.instance",
            "environment": scope["environment"],
            "owner": scope["owner"],
            "service": "finops-api",
            "region": scope["region"],
            "cost_amount": 12.54,
            "cost_currency": "USD",
            "usage_quantity": 24,
            "usage_unit": "hour",
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "tags": {"cost_center": scope["cost_center"]},
        }
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description="Run bootstrap GCP collectors")
    parser.add_argument("--scope", required=True, type=Path, help="Path to GCP scope JSON")
    parser.add_argument("--output-dir", required=True, type=Path, help="Output directory")
    args = parser.parse_args()

    scope = json.loads(args.scope.read_text(encoding="utf-8"))
    args.output_dir.mkdir(parents=True, exist_ok=True)

    inventory = collect_inventory(scope)
    billing = collect_billing(scope)

    (args.output_dir / "inventory.json").write_text(json.dumps(inventory, indent=2), encoding="utf-8")
    (args.output_dir / "billing.json").write_text(json.dumps(billing, indent=2), encoding="utf-8")
    print(f"OK: wrote {len(inventory)} inventory and {len(billing)} billing records")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
