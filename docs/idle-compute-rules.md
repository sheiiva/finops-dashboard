# Idle Compute Detection Rules

## Purpose

Identify compute instances with sustained low utilization and quantify savings opportunity.

## Rule v1

- Resource type must be `compute.instance`
- `avg_cpu_percent < 10`
- `active_hours >= 24`

## Inputs

- `config/examples/compute-utilization.sample.json`

## Script

- `scripts/detect_idle_compute.py`

## Run

```bash
python scripts/detect_idle_compute.py \
  --input config/examples/compute-utilization.sample.json \
  --output tmp/detection/idle-compute-findings.json \
  --cpu-threshold 10 \
  --min-hours 24
```

## Output

- Idle findings list with:
  - `resource_id`
  - `avg_cpu_percent`
  - `active_hours`
  - `estimated_monthly_savings_usd`
  - `reason`
