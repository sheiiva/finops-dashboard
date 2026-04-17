# Priority Scoring Model

## Purpose

Rank optimization opportunities by combining savings impact, confidence, and execution effort.

## Formula

`priority_score = estimated_monthly_savings_usd * confidence_factor * effort_factor`

## Factors

- `confidence_factor`:
  - `high` = `1.0`
  - `medium` = `0.75`
  - `low` = `0.5`
- `effort_factor`:
  - `low` = `1.0`
  - `medium` = `0.7`
  - `high` = `0.4`

## Script

- `scripts/score_opportunities.py`

## Run

```bash
python scripts/score_opportunities.py \
  --input config/examples/opportunities.sample.json \
  --output tmp/detection/scored-opportunities.json
```

Output is sorted descending by `priority_score`.
