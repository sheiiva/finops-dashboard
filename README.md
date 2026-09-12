# FinOps and Cloud Waste Dashboard

[![Conventional Commits](https://img.shields.io/badge/Conventional%20Commits-1.0.0-%23FE5196?logo=conventionalcommits&logoColor=white)](https://conventionalcommits.org)

## Business Value

Native cloud consoles explain **where money is spent**. This project adds the execution layer: prioritized actions, explicit ownership, estimated savings, and a clear path to verify outcomes.

## What v1 demonstrates (portfolio showcase)

**Google Cloud–first** CSV demo — not a live billing login.

1. Public product UI (GitHub Pages): spend → trend → opportunities → owner action queue  
2. Same CSV feeds a local Prometheus + Grafana **evidence** stack for screenshots / client handoff  
3. Synthetic costs with **real Google Cloud service names and public service IDs**

Live site: https://sheiiva.github.io/finops-dashboard/

```bash
./scripts/local_dashboard_stack.sh up
./scripts/local_dashboard_stack.sh inject-csv
```

See `docs/local-dashboard-validation.md`.

## Version map

| Version | Scope |
|---|---|
| **v1** | Pages wow showcase + CSV pipeline + Grafana evidence (this release bar) |
| **v1.1** | Deeper sections (Pareto, savings lines, allocation, forecast) |
| **v2** | Live Google Cloud API / billing export streaming |
| **v3** | AWS / Azure adapters (later) |

## Interview / freelance positioning

Reusable FinOps accelerator template: product narrative on Pages, ops depth in repo (schema, adapters, detection, runbooks, CI). Starts on Google Cloud; multi-cloud is explicitly later.

## Directory layout

- `site/`: public product showcase  
- `config/examples/`: anonymized billing CSV + generated snapshot/metrics  
- `scripts/`: CSV→metrics/snapshot, collectors, detection helpers  
- `ops/grafana/`: local evidence dashboard provisioning  
- `docs/`: architecture, KPIs, runbooks, roadmap  
- `terraform/`: module skeleton for future platform resources  

## Delivery docs

- Roadmap: `docs/roadmap.md`  
- Architecture: `docs/architecture.md`  
- Getting started: `docs/getting-started.md`  
