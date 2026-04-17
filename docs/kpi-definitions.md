# KPI Definitions

## Executive KPIs

- `Monthly Cloud Spend (USD)`: Sum of cloud cost for the active month across providers.
- `Addressable Opportunity (USD)`: Sum of estimated monthly savings from currently open optimization findings.
- `Realized Savings MTD (USD)`: Sum of savings from actions completed in current month.
- `Spend Trend by Provider`: Daily spend grouped by provider (`gcp`, `aws`, `azure`).
- `Top Opportunity Types`: Opportunity value grouped by finding type (`idle_compute`, `orphaned_storage`, `rightsizing`).

## Ownership and Accountability KPIs

- `Open Actions by Owner`: Count of findings assigned to each owner.
- `Aging Actions > 14 Days`: Open findings with no state change for more than 14 days.
- `Priority Score Coverage`: Ratio of open findings with valid `priority_score`.
- `Tag Compliance`: Percentage of resources with mandatory tags.

## KPI Governance

- KPI formulas are immutable within a minor release.
- Any KPI formula change requires ADR entry and changelog note.
