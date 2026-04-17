# Runbook: Savings Verification

## Purpose

Prove that a remediation reduced or avoided cost using **evidence**, not estimates alone.

## Required evidence

| Evidence | Rule |
|----------|------|
| Before window | Cost or usage for same scope **7–30 days** before change (billing export or metric query). |
| After window | Same scope **7–30 days** after change, excluding unrelated churn. |
| Attribution | Scope filter: account, project, resource ID, or tag set documented. |
| Currency | Same currency; note FX if multi-currency. |

## Metric

- **Realized monthly savings** = baseline mean daily cost − post mean daily cost, scaled to 30 days, for comparable calendar periods.  
- Document **confidence** (high if single resource; medium if shared pool).

## Workflow

1. Capture baseline numbers from approved source (export CSV path or query ID).  
2. Capture post numbers after stabilization (minimum **7 days** unless resource deleted).  
3. Store evidence links in the closed finding or ticket.  
4. Roll up to executive dashboard `realized savings MTD` only after review.

## Rejection criteria

- No comparable before window.  
- Scope changed (new traffic, new SKU) without adjustment.  
- Savings only from one-time credits.
