# Multi-Cloud KPI Dashboard

## Artifact

- `dashboards/grafana/multi-cloud-kpi.dashboard.json`

## KPI parity

All providers must emit **same metric names** with `provider` label in `{gcp,aws,azure}`:

| KPI | PromQL shape |
|-----|----------------|
| Spend | `sum by(provider) (finops_monthly_spend_usd)` |
| Opportunity | `sum by(provider) (finops_opportunity_monthly_usd)` |
| Tag compliance floor | `min by(provider) (finops_tag_compliance_ratio)` |

Definitions align with `docs/kpi-definitions.md`; only grouping changes.

## Owner attribution

- Table panel expects `finops_action_queue` series or labels including `owner`, `provider`, and `resource_id` (same contract as team action queue).

## Validation checklist

- [ ] Each provider exports monthly spend with `provider` label  
- [ ] Opportunity metric uses identical rollup window across clouds  
- [ ] Tag compliance uses same mandatory tag set per `docs/tag-policy.md`  
- [ ] Spot-check one resource: `owner` matches normalized record after adapter mapping  

## Import

Grafana → Import → upload JSON → map Prometheus data source.
