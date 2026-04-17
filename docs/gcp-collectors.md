# GCP Collectors (Bootstrap)

This document defines bootstrap collectors for GCP inventory and billing signals.

## Files

- Collector script: `scripts/gcp_collectors.py`
- Scope example: `config/examples/gcp-scope.example.json`

## Purpose

- Provide deterministic collector outputs for early data-model integration.
- Validate normalized schema consumption before live API integration.

## Usage

```bash
python scripts/gcp_collectors.py \
  --scope config/examples/gcp-scope.example.json \
  --output-dir tmp/gcp-collector-output
```

Expected outputs:

- `tmp/gcp-collector-output/inventory.json`
- `tmp/gcp-collector-output/billing.json`

## Next Step

Replace stub record generation with live GCP API extraction in later implementation iterations.
