# Optimization Automation Backlog

Prioritization uses same mental model as `scripts/score_opportunities.py`: **impact × confidence × ease** (ease inverse of operational risk).

## Backlog

| ID | Automation | Impact | Risk | Ease | Notes |
|----|----------------|--------|------|------|--------|
| A1 | Idle compute auto-stop (tag-gated) | High | High | Low | Needs change window policy |
| A2 | Orphaned disk snapshot delete after N days | Medium | Medium | Medium | Finance sign-off on retention |
| A3 | Tag enforcement PR on non-compliant resources | Medium | Low | High | Good CI integration |
| A4 | Reserved instance / CUD recommendation export | High | Low | Medium | Provider APIs differ |
| A5 | Anomaly → ticket with owner from CMDB | Medium | Low | High | Routing only |

**Scoring (1–5 each):** multiply I×C×E / 125 to get rough rank.

| ID | I | C | E | Rank |
|----|---|---|---|------|
| A3 | 4 | 4 | 5 | 0.64 |
| A5 | 4 | 4 | 4 | 0.41 |
| A4 | 5 | 4 | 3 | 0.48 |
| A2 | 3 | 3 | 3 | 0.22 |
| A1 | 5 | 2 | 2 | 0.16 |

## Top candidates for next milestone (P7)

1. **A4** — aligns with multi-cloud expansion: implement recommendation export per provider, then consolidate KPIs.  
2. **A3** — low risk; reinforces governance already in CI.  
3. **A5** — closes loop from alert to work item without full remediation automation.

Work tracked under issues **#30–#32** for provider adapters and consolidated dashboard; A4/A5 feed same metrics plane.
