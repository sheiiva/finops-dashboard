# Roadmap

This roadmap maps GitHub milestones to delivery outcomes.

## P0 - Productization and Template Design

Deliverables:
- Reusable architecture definition
- Provider adapter contract
- Parameterized configuration schema
- Config schema validation utility and onboarding example

Outcome:
- New company onboarding by config only, no core rewrite.

## P1 - Discovery and Baseline

Deliverables:
- Scope matrix (accounts/regions/environments)
- Tagging policy and ownership model
- Baseline spend profile and optimization hypotheses
- Explicit out-of-scope register with rationale
- Compliance computation utility for mandatory tagging KPI
- Baseline report artifact with ranked optimization hypotheses

Outcome:
- Shared baseline for technical and business prioritization.

## P2 - Data Model and Collection (GCP)

Deliverables:
- Normalized schema v1
- GCP collectors (inventory, utilization, cost)
- Data quality and freshness checks
- Example normalized records for contract validation
- Collector runbook with scope input and generated artifacts
- Quality report artifact generated from normalized collector output

Outcome:
- Reliable telemetry foundation for optimization decisions.

## P3 - Waste Detection Engine

Deliverables:
- Idle compute rules
- Orphaned storage/artifact rules
- Priority scoring model
- Detection runbooks with sample inputs and generated findings

Outcome:
- Ranked, actionable savings opportunities.

## P4 - Dashboard and Alerting

Deliverables:
- Executive dashboard
- Team action queue dashboard
- Anomaly and compliance drift alerts

Outcome:
- Clear visibility from spend signals to owner-level action.

## P5 - Operationalization and Governance

Deliverables:
- FinOps cadence and RACI
- Runbooks for triage/remediation/verification
- CI governance controls

Outcome:
- Repeatable operating model with auditability.

## P6 - Hardening and Scale

Deliverables:
- Forecasting baseline
- Scale strategy documentation
- Automation backlog

Outcome:
- Platform readiness for larger data and team scope.

## P7 - Multi-Cloud Expansion

Deliverables:
- AWS adapter
- Azure adapter
- Consolidated cross-cloud dashboard

Outcome:
- Single FinOps framework across GCP, AWS, and Azure.
