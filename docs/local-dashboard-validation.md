# Local Dashboard Validation (Docker Compose)

Use this flow to get a visual dashboard validation environment in minutes.

## Prerequisites

- Docker with Compose plugin
- Open local ports: `3000`, `9090`, `9091`

## One-time commands

From repository root:

```bash
chmod +x scripts/local_dashboard_stack.sh scripts/inject_sample_metrics.sh
```

## Start stack

```bash
./scripts/local_dashboard_stack.sh up
```

## Inject sample metrics

```bash
./scripts/local_dashboard_stack.sh inject
```

Sample metrics source:

- `config/examples/finops-sample-metrics.prom`

## Open UIs

- Grafana: `http://localhost:3000` (`admin` / `admin`)
- Prometheus: `http://localhost:9090`
- Pushgateway: `http://localhost:9091`

## Grafana preconfigured (no manual setup)

Provisioning is automatic from:

- datasource: `ops/grafana/provisioning/datasources/datasource.yml`
- dashboards provider: `ops/grafana/provisioning/dashboards/dashboards.yml`
- preloaded dashboard: `ops/grafana/dashboards/finops-local-validation.dashboard.json`

After stack starts, open Grafana and go to dashboard:

- `FinOps Local Validation`

## Stop stack

```bash
./scripts/local_dashboard_stack.sh down
```
