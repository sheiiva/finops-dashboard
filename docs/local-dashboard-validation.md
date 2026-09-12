# Local Dashboard Validation (Docker Compose)

**v1 front door:** GitHub Pages product showcase (wow narrative) — see issue #86 / live site.  
**This doc:** optional **Grafana evidence** stack for screenshots/GIF and local validation.

v1 slim evidence sections: **A · B · C · F · G · J** (D/E/H/I/K → **v1.1**).

**Data path today:** manually filled / anonymized CSV (not live cloud).  
**v2 (later):** connect a cloud account and stream costs via provider APIs (#88).

## Prerequisites

- Docker with Compose plugin
- Open local ports: `3000`, `9090`, `9091`

## Start stack

```bash
chmod +x scripts/local_dashboard_stack.sh scripts/inject_sample_metrics.sh
./scripts/local_dashboard_stack.sh up
```

## Inject CSV demo metrics (recommended)

Uses anonymized fixture `config/examples/gcp-billing-services.sample.csv`:

```bash
./scripts/local_dashboard_stack.sh inject-csv
```

This regenerates:

- `config/examples/finops-csv-metrics.prom`
- `config/examples/finops-csv-messages.json`
- `ops/grafana/dashboards/finops-local-validation.dashboard.json`

then pushes metrics to Pushgateway.

## Open UIs

- Grafana: `http://localhost:3000` (`admin` / `admin`)
- Dashboard: **FinOps v1 Slim (CSV demo)** (folder FinOps)
- Prometheus: `http://localhost:9090`
- Pushgateway: `http://localhost:9091`

## Section map (v1)

| Section | What you should see |
|---|---|
| A | Invoice total, service count, opportunity $, top share |
| B | Cost-by-service bar + share table |
| C | MoM change gauge + New services table |
| F | Savings opportunities + mix by type |
| G | Prioritized action queue |
| J | Alert flags (spend spike / growth / open actions) |

Data is **synthetic / anonymized** — safe for demos and portfolio screenshots.

## Legacy / deferred injectors

```bash
./scripts/local_dashboard_stack.sh inject      # old multi-cloud .prom sample
./scripts/local_dashboard_stack.sh inject-gcp  # live GCP (deferred / #88)
```

## Stop stack

```bash
./scripts/local_dashboard_stack.sh down
```
