# FinOps Operating Cadence and RACI

## Cadence

| Rhythm | Focus | Outputs |
|--------|--------|---------|
| Weekly | Spend vs forecast, open actions, tag compliance | Week notes, reprioritized queue |
| Monthly | Savings realized, policy exceptions, roadmap | Monthly report, exception register update |
| Quarterly | KPI targets, tooling budget, RACI review | Quarter plan, adjusted thresholds |

## RACI

| Activity | Engineering | FinOps lead | Finance | Security / Gov | Exec sponsor |
|----------|-------------|-------------|---------|------------------|--------------|
| Scope and tagging policy | C | A | C | C | I |
| Dashboards and alerts | R | A | I | C | I |
| Anomaly triage | R | A | I | C | I |
| Remediation execution | R | C | I | I | I |
| Savings verification | C | A | R | I | I |
| Budget vs forecast sign-off | C | C | A | I | R |
| Exception approval | C | R | C | A | I |

- **R** = does work  
- **A** = accountable (one per row)  
- **C** = consulted  
- **I** = informed  

## Weekly meeting checklist

- [ ] Previous week actions: closed vs open, blockers named  
- [ ] Top spend movers by provider and service  
- [ ] New vs cleared anomalies and compliance drift  
- [ ] Top three optimization actions by `priority_score`  
- [ ] Tag compliance trend and exception queue  
- [ ] Decisions and owners for next week  

## Decision rights

- **Policy change** (tags, thresholds): FinOps lead proposes; governance approves exceptions.  
- **Production change** from optimization: owning team executes; FinOps tracks savings hypothesis.  
- **Budget / forecast**: Finance owns numbers; FinOps aligns technical drivers and narratives.
