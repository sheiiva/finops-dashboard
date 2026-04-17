# Data Quality and Freshness Checks

This document defines baseline checks for collector output quality.

## Scope

Checks apply to normalized records emitted by collectors before downstream scoring and dashboards.

## Metrics

- `completeness_percent`: records with all required fields populated
- `freshness_percent`: records within freshness SLA
- `null_field_violations`: records missing required values
- `stale_records`: records older than freshness SLA

## Script

- `scripts/data_quality_report.py`

## Usage

```bash
python scripts/data_quality_report.py \
  --input config/examples/normalized-cost-asset.example.json \
  --output tmp/quality/quality-report.json \
  --freshness-sla-minutes 180
```

## SLA Defaults

- Freshness SLA: `180` minutes
- Target completeness: `>= 95%`
- Target freshness: `>= 95%`
