# Baseline Spend and Waste Hypothesis Report

## Objective

Establish an initial spend baseline and ranked optimization hypotheses to guide early execution.

## Baseline Summary (Illustrative)

| Category | Monthly Spend (USD) | Share |
| --- | ---: | ---: |
| Compute | 32,000 | 45.7% |
| Managed Databases | 18,000 | 25.7% |
| Storage | 11,000 | 15.7% |
| Networking | 6,000 | 8.6% |
| Observability/Other | 3,000 | 4.3% |
| **Total** | **70,000** | **100%** |

## Top Spend Categories Identified

1. Compute
2. Managed Databases
3. Storage

These categories represent the highest leverage for initial optimization work.

## Ranked Waste Hypotheses

| Rank | Hypothesis | Category | Estimated Monthly Opportunity (USD) | Confidence |
| ---: | --- | --- | ---: | --- |
| 1 | Sustained idle/underutilized compute instances | Compute | 6,000 | High |
| 2 | Overprovisioned managed database tiers | Managed Databases | 3,500 | Medium |
| 3 | Orphaned snapshots and unattached volumes | Storage | 2,200 | Medium |
| 4 | Non-critical workloads in premium regions/SKUs | Compute/Networking | 1,500 | Low |

## Prioritization Notes

- Prioritize hypotheses by impact first, then confidence.
- Keep SLO guardrails explicit before rightsizing actions.
- Validate each hypothesis with sampled evidence before automation.
