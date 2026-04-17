# FinOps Dashboard Nomenclature, Objectives, Implementation Plan, and DoD

## 1) Nomenclature

This section defines shared terms used across engineering, SRE, and finance.

- **FinOps**: Cloud financial operations practice aligning engineering decisions with business cost outcomes.
- **Cloud Waste**: Spend with low or no business value (idle, orphaned, oversized, underutilized resources).
- **Cost Allocation**: Mapping cloud costs to accountable owners (team, product, environment, service).
- **Tag Compliance**: Percentage of resources that include mandatory cost-allocation tags.
- **Unit Economics**: Cost per meaningful business unit (e.g., per customer, per transaction, per environment).
- **Idle Resource**: Resource running but not delivering meaningful workload for a defined period.
- **Rightsizing**: Adjusting resource size/shape to measured demand while preserving SLOs.
- **Coverage KPI**: Portion of total spend represented by monitored and classified resources.
- **Savings Opportunity**: Estimated monthly amount recoverable from a specific action.
- **Realized Savings**: Verified cost reduction after implementing an optimization.
- **Forecast Accuracy**: Error margin between predicted monthly spend and actual spend.
- **Anomaly Detection**: Automatic detection of unusual spend spikes by scope (account, service, team, env).
- **Showback**: Cost visibility provided to teams without direct charge.
- **Chargeback**: Costs billed back to teams/business units based on allocation model.
- **SLO Guardrail**: Constraint ensuring cost optimizations do not degrade reliability objectives.
- **MTTR for Cost Events**: Time to diagnose and mitigate cost anomalies.
- **TCO (Total Cost of Ownership)**: Full lifecycle cost including infra, tooling, support, and operations effort.
- **Runbook**: Operational procedure for recurring incident/optimization workflows.

## 2) Objectives

### 2.1 Business Objectives

1. Reduce avoidable cloud spend by identifying and prioritizing highest-value waste-removal actions.
2. Increase cost accountability with team-level and service-level cost visibility.
3. Improve planning confidence through spend forecasting and anomaly alerting.
4. Establish repeatable FinOps operating model usable by engineering and finance stakeholders.

### 2.2 Technical Objectives

1. Build reliable telemetry and cost-ingestion pipeline for cloud asset/cost signals.
2. Provide actionable Grafana dashboards with clear priority rankings and estimated monthly impact.
3. Automate waste-detection logic for idle, orphaned, and oversized resources.
4. Enforce secure, auditable, and reproducible deployment via Terraform + CI checks.
5. Document runbooks and KPI definitions to support operational continuity.
6. Package solution as reusable template with parameterized provider/account/environment inputs.
7. Implement provider adapter model to support GCP first, then AWS and Azure.

### 2.3 Success Metrics (Initial Targets)

- **Coverage KPI**: >= 90% of monthly cloud spend mapped to owner tags.
- **Tag Compliance**: >= 95% on mandatory cost tags.
- **Anomaly Lead Time**: spend spike alert generated within 60 minutes of threshold breach.
- **Top-N Opportunities**: dashboard lists top 20 optimization actions by potential monthly savings.
- **Realized Savings Velocity**: at least 2 prioritized actions executed per sprint after go-live.
- **Forecast Error (Month-end)**: <= 10% absolute error at account and team level.

## 3) Detailed Implementation Plan

## Phase 0 - Portfolio Productization and Template Design

### Scope
- Define this repository as a reusable company-agnostic accelerator, not a single-tenant implementation.
- Create parameter model for organization, billing scopes, accounts/subscriptions/projects, environments, and tags.
- Design provider adapter contract so collection and detection logic can plug cloud-specific modules.

### Deliverables
- Template architecture document (core modules + provider adapters + shared governance layer).
- Configuration schema for reusable onboarding (`org`, `env`, `provider`, `billing_scope`, `tag_policy`).
- Reference tenant configuration example for local/demo deployment.

### Exit Criteria
- New company onboarding requires configuration updates, not core code rewrites.
- Core logic runs with mock adapter interface independent of cloud provider.

## Phase 1 - Discovery and Baseline

### Scope
- Confirm cloud providers/accounts/environments in scope.
- Define mandatory tags and ownership model.
- Establish baseline monthly spend and known pain points.

### Deliverables
- Scope matrix (accounts, regions, clusters, services).
- Baseline report with top spend categories and current tag coverage.
- Approved KPI list and dashboard audience map.

### Exit Criteria
- Stakeholders validate scope and baseline.
- KPI definitions accepted by engineering + finance.

## Phase 2 - Data Model and Collection

### Scope
- Implement data collection scripts for asset inventory + utilization + cost signals.
- Define normalized schema for ingestion (resource metadata, usage stats, cost dimensions).
- Build secure authentication and least-privilege access for API collectors.
- Implement GCP adapter first as baseline provider implementation.

### Deliverables
- Versioned schema contract in `docs/`.
- Python collectors in `scripts/` with retries, backoff, and structured logs.
- Data quality checks (nulls, tag completeness, timestamp sanity).

### Exit Criteria
- Daily collection jobs run successfully for 7 consecutive days.
- Data completeness >= 95% for in-scope resources.

## Phase 3 - Waste Detection Engine

### Scope
- Implement rule sets for:
  - Idle compute
  - Orphaned storage/artifacts
  - Kubernetes rightsizing opportunities
  - Non-compliant resource configurations tied to waste
- Compute estimated monthly savings per finding.
- Add confidence score and owner routing metadata.

### Deliverables
- Detection modules with unit tests.
- Rule thresholds documented with rationale.
- Priority scoring model (impact x confidence x ease).

### Exit Criteria
- False-positive review completed with platform owners.
- Top opportunities are reproducible from raw inputs.

## Phase 4 - Dashboard and Alerting

### Scope
- Build Grafana dashboards for:
  - Executive summary (trend + total opportunity)
  - Team/service breakdown
  - Action queue with owner and expected savings
  - Anomaly timeline and incident linkage
- Configure alerting for spend anomalies and tag compliance drift.

### Deliverables
- Dashboard JSON/provisioning via IaC where possible.
- Alert rules with severity levels and notification paths.
- “How to read this dashboard” documentation.

### Exit Criteria
- Stakeholders can navigate from aggregate view to actionable item in <= 3 clicks.
- Alert routing validated in non-production and production dry run.

## Phase 5 - Operationalization and Governance

### Scope
- Define weekly FinOps review cadence (engineering + finance + product).
- Create runbooks for triage, optimization execution, and savings verification.
- Add CI/CD controls (format/lint/test/security checks).
- Implement change logs for rule updates and threshold changes.

### Deliverables
- Operating model and RACI in `docs/`.
- Runbooks with escalation paths and rollback guidance.
- Governance checklist for policy and security controls.

### Exit Criteria
- First review cycle completed end-to-end with tracked decisions.
- Optimization actions produce measurable and validated savings.

## Phase 6 - Hardening and Scale (Post-MVP)

### Scope
- Add forecasting models and seasonality support.
- Expand to multi-account / multi-region rollups.
- Introduce chargeback/showback exports for finance systems.
- Improve detection with historical behavior and confidence calibration.

### Deliverables
- Forecast module and accuracy dashboard.
- Scaled architecture guidance for data volume growth.
- Backlog of optimization automation candidates.

## Phase 7 - Multi-Cloud Expansion (GCP -> AWS -> Azure)

### Scope
- Add AWS and Azure adapters implementing same normalized data contract used by GCP.
- Keep waste rules provider-agnostic where possible, with provider-specific override rules when required.
- Build cross-cloud dashboards for consolidated view and cloud-specific drill-down.
- Harmonize identity and access patterns for least-privilege collection in each provider.

### Deliverables
- `gcp`, `aws`, and `azure` collector adapters with parity matrix.
- Cross-cloud mapping reference (service families, pricing dimensions, and terminology alignment).
- Validation suite proving same KPI formulas work across all supported providers.

### Exit Criteria
- Same template deploys to at least one GCP, one AWS, and one Azure scope by config only.
- Executive dashboard reports consolidated opportunities across providers with owner attribution.

## 4) Definition of Done (DoD)

## 4.1 Product DoD

Project is done when all criteria below are met:

1. Dashboard surfaces prioritized optimization opportunities with monthly USD estimates.
2. At least 90% of in-scope spend is visible with owner mapping.
3. Anomaly detection and alerting are active with tested routing.
4. Runbooks exist for detection triage, remediation, and savings validation.
5. Stakeholders (engineering + finance) complete one successful review cycle using produced artifacts.

## 4.2 Engineering DoD

- IaC is modular, reviewed, and reproducible (`terraform/`).
- Scripts are linted/tested and include structured logs + failure handling (`scripts/`).
- Security controls enforced: no hardcoded secrets, least privilege, encrypted transport/storage.
- CI gates pass: format, lint, tests, policy/security scans.
- All key assumptions, thresholds, and formulas documented.

## 4.3 Operations DoD

- On-call/SRE can operate system from runbook without tribal knowledge.
- Monitoring covers collector health, data freshness, dashboard availability, and alert throughput.
- Backup/rollback procedures documented and tested for critical components.
- Incident and change history process established for auditability.

## 4.4 Documentation DoD

- `README.md` stays concise and business-facing.
- `docs/` contains:
  - KPI glossary
  - Detection logic reference
  - Dashboard specification
  - Operating model and RACI
  - Runbooks and escalation policy
- Documentation reviewed and approved by engineering and finance representatives.

## 5) Immediate Next Actions

1. Confirm mandatory tag schema and ownership mapping.
2. Prioritize initial detection rules (idle compute, orphaned storage, K8s rightsizing).
3. Define first dashboard cut and acceptance criteria.
4. Schedule recurring FinOps review meeting and ownership.
