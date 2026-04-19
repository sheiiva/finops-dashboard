"""AWS adapter: CUR-style rows to normalized cost asset records."""

from __future__ import annotations

from .base import ProviderAdapter
from .normalize_utils import coalesce_tags, is_normalized, to_iso_z


class AWSAdapter(ProviderAdapter):
    provider = "aws"

    def fetch_inventory(self, scope: dict) -> list[dict]:
        return []

    def fetch_utilization(self, scope: dict) -> list[dict]:
        return []

    def fetch_costs(self, scope: dict) -> list[dict]:
        return []

    def normalize(self, records: list[dict]) -> list[dict]:
        return [_normalize_one(r) for r in records]

    def healthcheck(self) -> dict:
        return {"provider": self.provider, "status": "ok", "ready": True, "errors": []}


def _normalize_one(raw: dict) -> dict:
    if is_normalized(raw) and raw.get("provider") == "aws":
        return raw

    rid = raw.get("resource_id") or raw.get("line_item_resource_id") or ""
    cost = float(raw.get("line_item_unblended_cost") or raw.get("cost_amount") or 0)
    ts_raw = raw.get("timestamp") or raw.get("line_item_usage_start_date") or ""
    if not ts_raw:
        raise ValueError("AWS row missing line_item_usage_start_date or timestamp")

    tags = coalesce_tags(raw)
    env = tags.get("environment") or tags.get("env") or "unknown"
    owner = tags.get("owner") or "unassigned"

    cur = str(raw.get("line_item_currency_code") or raw.get("cost_currency") or "USD")[:3].upper()

    out = {
        "provider": "aws",
        "resource_id": rid,
        "resource_type": raw.get("resource_type")
        or raw.get("line_item_line_item_type")
        or "aws.unknown",
        "environment": env,
        "owner": owner,
        "service": raw.get("product_servicecode") or raw.get("service") or "unknown",
        "region": raw.get("product_region") or raw.get("region") or "unknown",
        "cost_amount": cost,
        "cost_currency": cur,
        "usage_quantity": float(raw.get("line_item_usage_amount") or raw.get("usage_quantity") or 0),
        "usage_unit": raw.get("line_item_usage_type") or raw.get("usage_unit") or "unit",
        "timestamp": to_iso_z(ts_raw),
        "tags": tags,
    }
    return out
