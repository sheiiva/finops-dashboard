"""Shared helpers for provider normalization."""

from __future__ import annotations

from datetime import UTC, datetime

NORM_KEYS = frozenset(
    {
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
    }
)


def is_normalized(record: dict) -> bool:
    return NORM_KEYS.issubset(record.keys()) and record.get("provider") in ("gcp", "aws", "azure")


def to_iso_z(ts: str) -> str:
    """Normalize timestamp string to RFC3339 with Z suffix."""
    s = ts.strip().replace("Z", "+00:00")
    dt = datetime.fromisoformat(s)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    return dt.astimezone(UTC).isoformat().replace("+00:00", "Z")


def coalesce_tags(raw: dict, prefix: str = "resource_tags_user_") -> dict[str, str]:
    """Extract user tags from flattened CUR-style keys."""
    tags: dict[str, str] = {}
    for k, v in raw.items():
        if not k.startswith(prefix) or v in (None, ""):
            continue
        tags[k[len(prefix) :].lower().replace("_", "-")] = str(v)
    return tags
