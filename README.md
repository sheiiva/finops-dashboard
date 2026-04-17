# FinOps and Cloud Waste Dashboard

[![Conventional Commits](https://img.shields.io/badge/Conventional%20Commits-1.0.0-%23FE5196?logo=conventionalcommits&logoColor=white)](https://conventionalcommits.org)

## Business Value

This project provides direct cost savings by detecting cloud waste, quantifying monthly loss, and presenting prioritized optimization opportunities for engineering and finance stakeholders.

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
