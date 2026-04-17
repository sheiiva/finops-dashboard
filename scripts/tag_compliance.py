#!/usr/bin/env python3
"""Compute mandatory tag compliance from a JSON resource list."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


REQUIRED_TAGS = ("owner", "environment", "service", "cost_center")


def load_resources(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("Input JSON must be a list of resource objects")
    return data


def is_compliant(resource: dict) -> bool:
    tags = resource.get("tags", {})
    if not isinstance(tags, dict):
        return False
    return all(isinstance(tags.get(k), str) and tags.get(k).strip() for k in REQUIRED_TAGS)


def main() -> int:
    parser = argparse.ArgumentParser(description="Compute tag compliance")
    parser.add_argument("resources_json", type=Path, help="Path to resources JSON list")
    args = parser.parse_args()

    resources = load_resources(args.resources_json)
    total = len(resources)
    compliant = sum(1 for r in resources if is_compliant(r))
    percent = 100.0 if total == 0 else (compliant / total) * 100
    print(json.dumps({"total": total, "compliant": compliant, "compliance_percent": round(percent, 2)}))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # pragma: no cover
        print(f"ERROR: {exc}")
        raise SystemExit(1)
