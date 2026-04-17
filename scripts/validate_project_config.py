#!/usr/bin/env python3
"""
Minimal config validation utility for project-config JSON files.

This script intentionally performs a lightweight validation aligned with
required schema fields so the project can bootstrap without extra dependencies.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ALLOWED_PROVIDERS = {"gcp", "aws", "azure", "multi"}
ALLOWED_ENFORCEMENT_MODES = {"audit", "enforce"}
REQUIRED_FIELDS = {"organization", "environment", "provider", "billing_scope", "tag_policy"}


def _load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in {path}: {exc}") from exc


def validate_config(config: dict) -> list[str]:
    errors: list[str] = []

    missing = sorted(REQUIRED_FIELDS - set(config.keys()))
    if missing:
        errors.append(f"Missing required fields: {', '.join(missing)}")

    for field in ("organization", "environment", "billing_scope"):
        value = config.get(field)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"Field '{field}' must be a non-empty string")

    provider = config.get("provider")
    if provider not in ALLOWED_PROVIDERS:
        errors.append(f"Field 'provider' must be one of: {', '.join(sorted(ALLOWED_PROVIDERS))}")

    tag_policy = config.get("tag_policy")
    if not isinstance(tag_policy, dict):
        errors.append("Field 'tag_policy' must be an object")
        return errors

    required_tags = tag_policy.get("required_tags")
    if not isinstance(required_tags, list) or not required_tags:
        errors.append("Field 'tag_policy.required_tags' must be a non-empty array")
    else:
        for tag in required_tags:
            if not isinstance(tag, str) or not tag.strip():
                errors.append("Each tag in 'tag_policy.required_tags' must be a non-empty string")
                break

    mode = tag_policy.get("enforcement_mode")
    if mode not in ALLOWED_ENFORCEMENT_MODES:
        errors.append(
            "Field 'tag_policy.enforcement_mode' must be one of: "
            + ", ".join(sorted(ALLOWED_ENFORCEMENT_MODES))
        )

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate project config JSON")
    parser.add_argument("config_path", type=Path, help="Path to config JSON file")
    args = parser.parse_args()

    config = _load_json(args.config_path)
    errors = validate_config(config)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print(f"OK: {args.config_path} passed validation")
    return 0


if __name__ == "__main__":
    sys.exit(main())
