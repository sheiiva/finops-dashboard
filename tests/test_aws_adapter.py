"""Tests for AWS adapter normalization."""

import json
from pathlib import Path

from scripts.adapters.aws import AWSAdapter


def test_normalize_cur_sample_matches_contract() -> None:
    raw = json.loads(
        Path("config/examples/aws-cur-row.sample.json").read_text(encoding="utf-8")
    )
    out = AWSAdapter().normalize([raw])[0]
    assert out["provider"] == "aws"
    assert out["resource_id"].startswith("arn:aws:ec2:")
    assert out["environment"] == "prod"
    assert out["owner"] == "team-platform"
    assert out["cost_amount"] == 42.5
    assert out["cost_currency"] == "USD"
    assert out["timestamp"].endswith("Z")
    assert "environment" in out["tags"]
