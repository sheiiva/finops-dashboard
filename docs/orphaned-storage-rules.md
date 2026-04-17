# Orphaned Storage and Artifact Detection Rules

## Purpose

Identify unattached or stale storage artifacts that generate avoidable cost.

## Rule v1

- Include storage types:
  - `storage.disk`
  - `storage.snapshot`
  - `storage.bucket`
- Mark as orphaned when:
  - disk/snapshot is not attached
  - bucket has `last_access_days > 90`

## Inputs

- `config/examples/storage-artifacts.sample.json`

## Script

- `scripts/detect_orphaned_storage.py`

## Run

```bash
python scripts/detect_orphaned_storage.py \
  --input config/examples/storage-artifacts.sample.json \
  --output tmp/detection/orphaned-storage-findings.json
```

## Output

- Findings include:
  - `resource_id`
  - `resource_type`
  - `last_access_days`
  - `estimated_monthly_savings_usd`
  - `reason`
