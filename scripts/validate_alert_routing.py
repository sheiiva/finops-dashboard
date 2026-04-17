#!/usr/bin/env python3
"""Validate alert routing definitions for mandatory FinOps alerts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

REQUIRED_ALERTS = {"FinOpsSpendAnomalyHigh", "FinOpsTagComplianceDrift"}


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate alert routing config")
    parser.add_argument("--input", required=True, type=Path)
    args = parser.parse_args()

    payload = json.loads(args.input.read_text(encoding="utf-8"))
    routes = payload.get("routes", [])
    if not isinstance(routes, list):
        raise SystemExit("ERROR: routes must be a list")

    seen: set[str] = set()
    for route in routes:
        alert = route.get("alert")
        channel = route.get("channel")
        owner = route.get("owner")
        if not alert or not channel or not owner:
            raise SystemExit("ERROR: each route requires alert, channel, and owner")
        seen.add(str(alert))

    missing = sorted(REQUIRED_ALERTS - seen)
    if missing:
        raise SystemExit(f"ERROR: missing required alert routes: {', '.join(missing)}")

    print(f"OK: validated {len(routes)} routes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
