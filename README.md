# FinOps and Cloud Waste Dashboard

[![Conventional Commits](https://img.shields.io/badge/Conventional%20Commits-1.0.0-%23FE5196?logo=conventionalcommits&logoColor=white)](https://conventionalcommits.org)

## Business Value

This project provides direct cost savings by detecting cloud waste, quantifying monthly loss, and presenting prioritized optimization opportunities for engineering and finance stakeholders.

## Why This Exists Beyond Native Cloud Cost Dashboards

Google Cloud already provides strong cost visibility. This project complements it by adding an execution layer: prioritized actions, explicit ownership, estimated savings per action, and operational governance to ensure recommendations are implemented without breaking reliability targets.

In short, native dashboards explain **where money is spent**; this project drives **what to do next, who does it, and how savings are verified**.

## Interview Portfolio Positioning

This repository is designed as a reusable FinOps accelerator template for real client delivery. It demonstrates platform engineering depth (IaC, observability, security, automation) and operating-model maturity (ownership, governance, runbooks, measurable outcomes), not only dashboard creation.

The implementation path starts with GCP and then extends to AWS and Azure through a provider adapter model so the same framework can be parameterized and reused across companies.

## Visual Portfolio Demo

- GitHub Pages site: `https://sheiiva.github.io/finops-dashboard/`
- Source: `site/`
- Deployment workflow: `.github/workflows/pages.yml`

## Technical Stack

- Prometheus and Grafana deployed with Helm
- Python-based cost discovery scripts using cloud SDKs
- Cloud asset analysis for unused storage, idle compute, and oversizing
- Kubernetes resource-rightsizing checks for non-compliant workloads
- Savings-focused dashboarding with estimated monthly USD impact

## Directory Layout

- `terraform/`: dashboard platform and monitoring IaC baseline
- `scripts/`: data collection and enrichment logic for waste detection
- `docs/`: KPI definitions, dashboard specifications, and operating model

## Delivery and Governance

- Roadmap and milestones: `docs/roadmap.md`
- Architecture and adapter model: `docs/architecture.md`
- Local bootstrap steps: `docs/getting-started.md`
- Decision records: `docs/decision-log/`
- Contribution workflow: `CONTRIBUTING.md`
