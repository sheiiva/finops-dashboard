"""Tests for Azure adapter normalization."""

import json
from pathlib import Path

from scripts.adapters.azure import AzureAdapter


def test_normalize_cost_row_sample() -> None:
    raw = json.loads(
        Path("config/examples/azure-cost-row.sample.json").read_text(encoding="utf-8")
    )
    out = AzureAdapter().normalize([raw])[0]
    assert out["provider"] == "azure"
    assert "/subscriptions/" in out["resource_id"]
    assert out["environment"] == "prod"
    assert out["owner"] == "team-data"
    assert out["cost_amount"] == 55.0
    assert out["cost_currency"] == "USD"
    assert out["usage_quantity"] == 24.0
    assert out["timestamp"].endswith("Z")
