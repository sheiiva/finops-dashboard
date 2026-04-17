# Executive Dashboard

## Artifact

- Dashboard JSON: `dashboards/grafana/executive-cost-opportunity.dashboard.json`

## Purpose

Provide leadership-level visibility across spend trend, optimization opportunity size, and realized savings.

## KPI Links

All KPI formulas used by this dashboard are defined in:

- `docs/kpi-definitions.md`

## Drill-Down Path

1. Start from executive aggregate panels (spend, opportunity, realized savings).
2. Drill down by provider from spend trend panel.
3. Drill down by opportunity type from top opportunity panel.
4. Jump to team action queue dashboard for owner-level execution.

## Import Example (Grafana)

1. Open Grafana dashboard import.
2. Upload `dashboards/grafana/executive-cost-opportunity.dashboard.json`.
3. Map data source to the FinOps metrics backend.
