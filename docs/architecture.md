# Architecture Overview

## Intent

This project is a reusable FinOps accelerator built around a provider-agnostic core and cloud-specific adapters.

## System Diagram

```mermaid
flowchart LR
    subgraph Providers
      GCP[GCP APIs / Billing Export]
      AWS[AWS Cost & Usage + APIs]
      AZ[Azure Cost Mgmt + APIs]
      K8S[Kubernetes Metrics]
    end

    subgraph Collectors
      ADGCP[GCP Adapter]
      ADAWS[AWS Adapter]
      ADAZ[Azure Adapter]
      ADK8S[K8s Adapter]
    end

    subgraph Core
      NORM[Normalized Data Model]
      RULES[Waste Detection Rules]
      SCORE[Priority Scoring]
      GOV[Governance Layer]
    end

    subgraph Outputs
      DASH[Grafana Dashboards]
      ALERT[Alerting]
      TASKS[Issue/PR Action Queue]
      REPORT[FinOps Reports]
    end

    GCP --> ADGCP
    AWS --> ADAWS
    AZ --> ADAZ
    K8S --> ADK8S

    ADGCP --> NORM
    ADAWS --> NORM
    ADAZ --> NORM
    ADK8S --> NORM

    NORM --> RULES --> SCORE
    SCORE --> DASH
    SCORE --> ALERT
    SCORE --> TASKS
    SCORE --> REPORT
    GOV --> RULES
    GOV --> DASH
```

## Key Design Principles

- Provider adapters isolate API differences.
- Core rules/scoring remain reusable across clouds.
- Governance artifacts (runbooks, review cadence, DoD) are first-class.
- Security by default: least privilege, no secrets in code, auditable automation.

## Adapter Contract

Provider adapter contract reference:

- `docs/provider-adapter-contract.md`
- `scripts/adapters/base.py`
