"""Azure adapter: cost export rows to normalized cost asset records."""

from __future__ import annotations

import json

from .base import ProviderAdapter
from .normalize_utils import is_normalized, to_iso_z


class AzureAdapter(ProviderAdapter):
    provider = "azure"

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


def _parse_tags(raw: dict) -> dict[str, str]:
    if "tags" in raw and isinstance(raw["tags"], dict):
        return {str(k).lower(): str(v) for k, v in raw["tags"].items() if v is not None}
    if "Tags" in raw and isinstance(raw["Tags"], str) and raw["Tags"].strip():
        try:
            data = json.loads(raw["Tags"])
            if isinstance(data, dict):
                return {str(k).lower(): str(v) for k, v in data.items()}
        except json.JSONDecodeError:
            return {}
    return {}


def _normalize_one(raw: dict) -> dict:
    if is_normalized(raw) and raw.get("provider") == "azure":
        return raw

    tags = _parse_tags(raw)
    env = (
        tags.get("environment")
        or tags.get("env")
        or raw.get("environment")
        or "unknown"
    )
    owner = tags.get("owner") or raw.get("owner") or "unassigned"

    rid = raw.get("resource_id") or raw.get("ResourceId") or ""
    ts_raw = raw.get("timestamp") or raw.get("UsageDate") or raw.get("Date") or ""
    if not ts_raw:
        raise ValueError("Azure row missing UsageDate or timestamp")

    cost = float(raw.get("CostInBillingCurrency") or raw.get("cost_amount") or 0)
    cur = str(raw.get("BillingCurrencyCode") or raw.get("cost_currency") or "USD")[:3].upper()

    qty = float(raw.get("ConsumedQuantity") or raw.get("usage_quantity") or 1.0)
    unit = raw.get("UnitOfMeasure") or raw.get("usage_unit") or "unit"

    out = {
        "provider": "azure",
        "resource_id": rid,
        "resource_type": raw.get("ResourceType") or raw.get("resource_type") or "azure.unknown",
        "environment": env,
        "owner": owner,
        "service": raw.get("ServiceName") or raw.get("service") or "unknown",
        "region": raw.get("ResourceLocation") or raw.get("region") or "unknown",
        "cost_amount": cost,
        "cost_currency": cur,
        "usage_quantity": qty,
        "usage_unit": unit,
        "timestamp": to_iso_z(str(ts_raw)),
        "tags": tags,
    }
    return out
