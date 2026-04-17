# Alerting Runbook

## Alert Rules

- Prometheus rule file: `alerts/prometheus/finops-alerts.yaml`
- Spend anomaly threshold: 25% above 14-day average sustained for 30 minutes
- Tag compliance drift threshold: compliance ratio below 90% sustained for 1 hour

## Routing Configuration

- Sample routing map: `config/examples/alert-routing.sample.json`
- Routing validation script: `scripts/validate_alert_routing.py`

## Validate Routing

```bash
python scripts/validate_alert_routing.py \
  --input config/examples/alert-routing.sample.json
```

## Notification Policy

- `FinOpsSpendAnomalyHigh` routes to FinOps Slack alert channel.
- `FinOpsTagComplianceDrift` routes to governance on-call channel.

## Triage Steps

1. Confirm alert integrity against source metrics.
2. Identify impacted provider/account scope.
3. Open or update remediation issue with owner and ETA.
4. Track closure and post-incident KPI impact.
